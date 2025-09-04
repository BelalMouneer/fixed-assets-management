from modules.models.models import Account, ExpenseTransaction, PurchaseTransaction, SalesTransaction
from sqlalchemy import select, or_, func
from ..exceptions.account import AccountExistsException, ParentNotFoundException, AccountNotFoundException
from werkzeug.exceptions import BadRequest
from modules.models.models import DailyEntries


def create_account_in_account_tree(session, body):
  try:
    # Ensure root accounts exist
    validate_root_accounts(session)
    
    name, parent_id, nature, cc_required, account_type = extract_body(body)
    check_if_account_exist(session, name.strip())
    
    # Prevent creating additional root accounts
    if parent_id is None:
      raise BadRequest("Cannot create new root accounts. Only use the 4 standard root accounts.")
    
    parent = get_parent_account_with_id(session, parent_id)
    
    # Get the root account for this parent
    root_account = get_root_account(session, parent)
    
    # Apply nature validation rules based on root account
    if root_account.name.lower() == "assets":
      # Assets and children must be debit
      if nature and nature != "debit":
        raise BadRequest("Accounts under Assets must have 'debit' nature")
      nature = "debit"
      
      # Validate account_type for Assets
      if account_type and account_type != "balance_sheet":
        raise BadRequest("Accounts under Assets must have 'balance_sheet' account type")
      account_type = "balance_sheet"
    
    elif root_account.name.lower() == "liability & equity":
      # Liability & Equity and children must be credit
      if nature and nature != "credit":
        raise BadRequest("Accounts under Liability & Equity must have 'credit' nature")
      nature = "credit"
      
      # Validate account_type for Liability & Equity
      if account_type and account_type != "balance_sheet":
        raise BadRequest("Accounts under Liability & Equity must have 'balance_sheet' account type")
      account_type = "balance_sheet"
    
    elif root_account.name.lower() == "expenses":
      # Expenses children default to debit if not specified
      if not nature:
        nature = "debit"
        
      # Validate account_type for Expenses
      if account_type and account_type != "p&l":
        raise BadRequest("Accounts under Expenses must have 'p&l' account type")
      account_type = "p&l"
    
    elif root_account.name.lower() == "revenue":
      # Revenue children default to credit if not specified
      if not nature:
        nature = "credit"
        
      # Validate account_type for Revenue
      if account_type and account_type != "p&l":
        raise BadRequest("Accounts under Revenue must have 'p&l' account type")
      account_type = "p&l"
    
    new_account = fill_new_account_info(session, name, nature, parent, cc_required, account_type)
    add_and_commit(session, new_account)
    return new_account.to_dict()
  except (BadRequest, AccountExistsException, ParentNotFoundException) as e:
    # Re-raise already handled exceptions
    raise
  except Exception as e:
    # Handle database and other unexpected errors
    session.rollback()
    raise BadRequest(f"Database error: {str(e)}")

def get_account_tree(session):
  stmt = select(Account).where(Account.parent_id == None)
  return get_all_accounts_from_stmt(session, stmt)

def update_account(session, account_id, update_fields):
  """
  Update account information. Can update name, cc_required, and account_type.
  
  Args:
    session: Database session
    account_id: ID of the account to update
    update_fields: Dictionary of fields to update
  
  Returns:
    Dictionary with result message
  """
  if not isinstance(update_fields, dict):
    raise BadRequest("Update fields must be provided as a dictionary")
  
  account = get_single_account(session, account_id)
  changes = []
  
  # Handle name update if provided
  if 'name' in update_fields:
    if not isinstance(update_fields['name'], str):
      raise BadRequest("Account name must be a string")
    
    new_name = update_fields['name'].strip()
    if not new_name:
      raise BadRequest("Account name cannot be empty")
      
    if account.name.lower() != new_name.lower():
      # Check if the account has been used in any transactions
      related_entries = session.query(DailyEntries).filter(
        or_(DailyEntries.debit == account.name, DailyEntries.credit == account.name)
      ).count()
      
      if related_entries > 0:
        raise BadRequest(f"Account with name [{account.name}] has existing transactions and cannot modify its name")
      
      # Check if the new name already exists
      check_if_account_exist(session, new_name)
      account.name = new_name
      changes.append("name")
  
  # Handle cost_center_required update
  if 'cc_required' in update_fields:
    # Validate input is strictly a boolean
    if not isinstance(update_fields['cc_required'], bool):
      raise BadRequest("Cost center requirement must be a boolean value (True or False)")
    
    cc_required = update_fields['cc_required']
    
    if account.cc_required != cc_required:
      # If turning off cc_required, check if account is used in a way that requires cost centers
      if not cc_required and account.cc_required:
        # Check if account is in a category that should always require cost centers
        is_purchase_or_expense = session.query(
          or_(
            session.query(PurchaseTransaction).filter_by(account_id=account.id).exists(),
            session.query(ExpenseTransaction).filter_by(account_id=account.id).exists()
          )
        ).scalar()
        
        # Check if account is COGS or rebate
        is_cogs_or_rebate = ("cost of goods sold" in account.name.lower() or "rebate" in account.name.lower())
        
        if is_purchase_or_expense or is_cogs_or_rebate:
          raise BadRequest(f"Cannot disable cost center requirement for account '{account.name}' because it is used for purchase, expense, COGS or rebates")
      
      account.cc_required = cc_required
      changes.append("cost center requirement")
  
  # Handle account_type update
  if 'account_type' in update_fields:
    # Allow None/empty to clear the account type
    if update_fields['account_type'] in (None, ''):
      if account.account_type != None:
        account.account_type = None
        changes.append("account type")
    else:
      if not isinstance(update_fields['account_type'], str):
        raise BadRequest("Account type must be a string")
        
      new_account_type = update_fields['account_type'].strip()
      
      # Validate account_type value
      if new_account_type not in ('balance_sheet', 'p&l'):
        raise BadRequest("Account type must be 'balance_sheet' or 'p&l'")
      
      if account.account_type != new_account_type:
        # Validate consistency between account type and root account
        root_account = get_root_account(session, account)
        
        # Check consistency: balance_sheet accounts should be under Assets or Liability & Equity
        if new_account_type == 'balance_sheet' and root_account.name not in ('Assets', 'Liability & Equity'):
          raise BadRequest(f"Cannot set account type to 'balance_sheet' for accounts under '{root_account.name}'. Only accounts under 'Assets' or 'Liability & Equity' can be balance sheet accounts.")
        
        # Check consistency: p&l accounts should be under Revenue or Expenses
        if new_account_type == 'p&l' and root_account.name not in ('Revenue', 'Expenses'):
          raise BadRequest(f"Cannot set account type to 'p&l' for accounts under '{root_account.name}'. Only accounts under 'Revenue' or 'Expenses' can be P&L accounts.")
        
        account.account_type = new_account_type
        changes.append("account type")
  
  if not changes:
    return {"message": "No changes detected"}
  
  session.commit()
  return {"message": f"Account updated successfully. Changed fields: {', '.join(changes)}"}

def get_single_account(session, account_id):
  account = session.query(Account).filter_by(id=account_id).first()
  if not account:
    raise AccountNotFoundException(f"Account with id [{account_id}] not exist")
  return account

def _update_account(account, new_account_name):
  account.name = new_account_name

def extract_body(body):
    nature = None
    parent_id = body.get('parent_id', None)
    cc_required = body.get('cc_required', False)
    account_type = body.get('account_type', None)
    
    if 'nature' in body:
        nature = body['nature'].strip().lower()
        
    if nature and nature not in ['debit', 'credit', 'both']:
        raise BadRequest("Nature should be debit, credit or both")
    
    if account_type and account_type not in ['balance_sheet', 'p&l']:
        raise BadRequest("Account type must be 'balance_sheet' or 'p&l'")
        
    return body['name'].strip(), parent_id, nature, cc_required, account_type

def check_if_account_exist(session, name: str):
  # Use func.lower() to ensure case-insensitive comparison with database values
  account = session.query(Account).filter(func.lower(Account.name) == name.lower()).first()
  if account:
    raise AccountExistsException(f"Account with name [{name}] already exists")

def get_parent_account_with_id(session, parent_id):
    if parent_id:
      parent = session.query(Account).filter_by(id=parent_id).first()
      if parent:
        return parent
      else:
        raise ParentNotFoundException(f"Parent account with id [{parent_id}] not found")
    else:
      return None

def fill_new_account_info(session, name, nature, parent: Account, cc_required=False, account_type=None):
    # Infer account_type if not provided but can be determined from the parent/root
    if account_type is None and parent:
        root_account = get_root_account(session, parent)
        if root_account.name in ('Assets', 'Liability & Equity'):
            account_type = 'balance_sheet'
        elif root_account.name in ('Revenue', 'Expenses'):
            account_type = 'p&l'
    
    # For expense accounts, set cc_required based on account name (COGS, etc.)
    if parent and cc_required is False:
        root_account = get_root_account(session, parent)
        if root_account.name == 'Expenses':
            # Automatically require cost centers for expense accounts except specific ones
            if "depreciation" not in name.lower() and "bank charges" not in name.lower():
                cc_required = True
        # Automatically require cost centers for COGS accounts
        if "cost of goods sold" in name.lower() or "rebate" in name.lower():
            cc_required = True
    
    return Account(
        name=name, 
        code=generate_code(session, parent), 
        parent=parent, 
        nature=nature, 
        cc_required=cc_required, 
        account_type=account_type
    )

def generate_code(session, parent: Account):
  if not parent:
    # Root accounts get codes like 1000, 2000, etc.
    last_sibling = session.query(Account).filter_by(parent_id=None).order_by(Account.code.desc()).first()
    if last_sibling:
      root_num = int(last_sibling.code) // 1000 + 1
      return str(root_num * 1000)
    else:
      return "1000"
  
  else:
    # Child accounts
    parent_code = parent.code
    # Find the last sibling's code
    last_sibling = session.query(Account).filter_by(parent_id=parent.id).order_by(Account.code.desc()).first()
    
    if last_sibling:
      if len(parent_code) == 4 and parent_code.endswith('000'):  # Root level (1000, 2000)
        # Extract the first digit and append new 3-digit suffix
        base = parent_code[0]
        last_suffix = int(last_sibling.code[-3:])
        new_suffix = str(last_suffix + 1).zfill(3)
        return base + new_suffix
      elif len(parent_code) == 4:  # First level child with 4-digit code (1001, 1002)
        # For second-level children of first-level accounts
        last_suffix = int(last_sibling.code[-3:])
        new_suffix = str(last_suffix + 1).zfill(3)
        return parent_code + new_suffix  # 1001 + 001 = 1001001
      else:
        # For deeper levels
        last_suffix = int(last_sibling.code[-3:])
        new_suffix = str(last_suffix + 1).zfill(3)
        return parent_code + new_suffix
    else:
      if len(parent_code) == 4 and parent_code.endswith('000'):  # Root level (1000, 2000)
        # Extract the first digit for first child
        base = parent_code[0]
        return base + "001"  # First child of 1000 becomes 1001
      else:
        # For all other levels
        return parent_code + "001"

def add_and_commit(session, new_account):
  session.add(new_account)
  session.commit()

def get_all_accounts_from_stmt(session, stmt):
  def compute_account_totals(account):
    # Get daily entries for the current account using account name matching
    account_entries = session.query(DailyEntries).filter(
      or_(DailyEntries.debit == account.name, DailyEntries.credit == account.name)
    ).all()
    # Calculate debit and credit amounts specifically for this account
    own_debit = sum(entry.debit_amount for entry in account_entries if entry.debit == account.name)
    own_credit = sum(entry.credit_amount for entry in account_entries if entry.credit == account.name)

    # Recursively process children accounts (if any)
    children = session.query(Account).filter_by(parent_id=account.id).order_by(Account.code).all()
    children_list = []
    children_total_debit = 0
    children_total_credit = 0
    for child in children:
      child_dict, child_debit, child_credit = compute_account_totals(child)
      children_list.append(child_dict)
      children_total_debit += child_debit
      children_total_credit += child_credit

    # Total for account is its own values plus sum of all its children
    total_debit = own_debit + children_total_debit
    total_credit = own_credit + children_total_credit

    account_dict = account.to_dict()
    # Report the calculated totals for this account (including children totals if any)
    account_dict['debit_amount'] = total_debit
    account_dict['credit_amount'] = total_credit
    # Optionally include children details if there are any
    if children_list:
      account_dict['children'] = children_list

    return account_dict, total_debit, total_credit

  accounts_list = []
  grand_total_debit = 0
  grand_total_credit = 0
  for row in session.execute(stmt):
    root = row[0]
    # Compute totals recursively for the root account and its descendants
    account_dict, total_debit, total_credit = compute_account_totals(root)
    accounts_list.append(account_dict)
    grand_total_debit += total_debit
    grand_total_credit += total_credit

  return {
    'accounts': accounts_list,
    'grand_total_debit': grand_total_debit,
    'grand_total_credit': grand_total_credit
  }

def get_account_with_balance(session, account_id):
    """Get account details with current balance"""
    # Move the import here to avoid circular import
    from modules.transactions.purchaseTransaction.utils import calculate_the_current_balance
    
    account = get_single_account(session, account_id)
    if not account:
        raise AccountNotFoundException(f"Account with id [{account_id}] not exist")
    
    # Get all daily entries
    daily_entries = session.query(DailyEntries).all()
    
    # Calculate balance using existing function
    balance = calculate_the_current_balance(session, daily_entries, account_id)
    
    # Get account details and add balance
    account_dict = account.to_dict()
    account_dict['balance'] = balance
    
    return account_dict

def delete_account(session, account_id):
  account = get_single_account(session, account_id)
  if not account:
    raise AccountNotFoundException(f"Account with id [{account_id}] not exist")
    
  # Check if the account is a parent of any other account
  if session.query(Account).filter_by(parent_id=account.id).count() > 0:
    raise BadRequest(f"Account with id [{account_id}] is a parent account and cannot be deleted")
    
  # Check if the account has been used in any transaction (daily entries)
  related_entries = session.query(DailyEntries).filter(
    or_(DailyEntries.debit == account.name, DailyEntries.credit == account.name)
  ).count()
  if related_entries > 0:
    raise BadRequest(f"Account with name [{account.name}] has been used in transactions so cannot be deleted")
    
  # Check if the account is referenced in sales transactions
  sales_count = session.query(SalesTransaction).filter_by(account_id=account.id).count()
  if sales_count > 0:
    raise BadRequest(f"Account with id [{account_id}] is referenced by {sales_count} sales transactions and cannot be deleted")
    
  # Check if the account is referenced in purchase transactions
  purchase_count = session.query(PurchaseTransaction).filter_by(account_id=account.id).count()
  if purchase_count > 0:
    raise BadRequest(f"Account with id [{account_id}] is referenced by {purchase_count} purchase transactions and cannot be deleted")
    
  # Check if the account is referenced in expense transactions
  expense_count = session.query(ExpenseTransaction).filter_by(account_id=account.id).count()
  if expense_count > 0:
    raise BadRequest(f"Account with id [{account_id}] is referenced by {expense_count} expense transactions and cannot be deleted")
    
  session.delete(account)
  session.commit()
  return account.to_dict()

def get_accounts_by_parent_name(session, parent_name):
  """
  Get all accounts that are under a specific parent account in a hierarchical structure.
  Returns the parent and all its descendants recursively.
  """
  # Find the parent account
  parent = session.query(Account).filter_by(name=parent_name).first()
  if not parent:
    raise AccountNotFoundException(f"Parent account with name [{parent_name}] not found")
  
  # Build hierarchical structure recursively
  def build_account_tree(account):
    result = account.to_dict()
    children = session.query(Account).filter_by(parent_id=account.id).all()
    
    if children:
      result['children'] = [build_account_tree(child) for child in children]
    else:
      result['children'] = []
      
    return result
  
  # Return the full hierarchical structure
  return build_account_tree(parent)

def validate_root_accounts(session):
    """Ensure the 4 root accounts exist, create them if they don't"""
    root_accounts = {
        "Assets": {"nature": "debit", "account_type": "balance_sheet", "cc_required": False},
        "Liability & Equity": {"nature": "credit", "account_type": "balance_sheet", "cc_required": False},
        "Expenses": {"nature": "debit", "account_type": "p&l", "cc_required": False},
        "Revenue": {"nature": "credit", "account_type": "p&l", "cc_required": False}
    }
    
    for name, props in root_accounts.items():
        account = session.query(Account).filter(
            Account.name == name,
            Account.parent_id == None
        ).first()
        
        if not account:
            new_account = Account(
                name=name,
                code=generate_code(session, None),
                nature=props["nature"],
                parent=None,
                cc_required=props["cc_required"],
                account_type=props["account_type"]
            )
            session.add(new_account)
        else:
            # Update existing root account with new fields if needed
            if account.account_type != props["account_type"]:
                account.account_type = props["account_type"]
            if account.cc_required != props["cc_required"]:
                account.cc_required = props["cc_required"]
    
    session.commit()

def get_root_account(session, account):
    """Get the root account for any account in the hierarchy"""
    current = account
    
    while current.parent_id is not None:
        current = session.query(Account).get(current.parent_id)
    
    return current
