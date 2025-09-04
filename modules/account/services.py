from .utils import create_account_in_account_tree, get_account_tree, update_account, delete_account, get_accounts_by_parent_name
from ..app import Session, app
from ..exceptions.account import *
from werkzeug.exceptions import BadRequest
from flask import request, json
from flask_restx import Resource
from .utils import get_account_with_balance
from modules.utils.pagination import paginate_query

class AccountResource(Resource):
  def post(self):
    session = Session()
    with session:
      try:
        body = request.json
        # Add validation for cc_required and account_type
        if 'cc_required' in body and not isinstance(body['cc_required'], bool):
          return app.response_class(
            response=json.dumps({'message': 'Cost center requirement must be a boolean value'}), 
            status=400, 
            mimetype='application/json'
          )
          
        if 'account_type' in body and body['account_type'] not in [None, '', 'balance_sheet', 'p&l']:
          return app.response_class(
            response=json.dumps({'message': 'Account type must be either "balance_sheet" or "p&l"'}), 
            status=400, 
            mimetype='application/json'
          )
          
        return app.response_class(
          response=json.dumps(create_account_in_account_tree(session, body)), 
          status=201, 
          mimetype='application/json'
        )
      except BadRequest as e:
        return app.response_class(
          response=json.dumps({'message': str(e)}), 
          status=400, 
          mimetype='application/json'
        )
      except AccountException as e:
        return app.response_class(
          response=json.dumps({'message': e.__str__()}), 
          status=e.status_code, 
          mimetype='application/json'
        )
      except Exception as e:
        return app.response_class(
          response=json.dumps({'message': e.__str__()}), 
          status=500, 
          mimetype='application/json'
        )

  def get(self):
    session = Session()
    with session:
        result = get_account_tree(session)  # returns the dict with 'accounts' & grand totals
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        paginated_accounts = paginate_query(result['accounts'], page, per_page)
        # Add the grand totals to the paginated result
        paginated_accounts['grand_total_debit'] = result['grand_total_debit']
        paginated_accounts['grand_total_credit'] = result['grand_total_credit']
        return app.response_class(
            response=json.dumps(paginated_accounts),
            status=200,
            mimetype='application/json'
        )

class AccountResourceUpdate(Resource):
  def put(self, account_id):
    session = Session()
    data = request.json
    
    # Check if any update data was provided
    if not data:
      return app.response_class(response=json.dumps({'message': 'No update data provided'}), status=400, mimetype='application/json')
    
    # Extract fields that can be updated
    update_fields = {}
    if 'name' in data:
      update_fields['name'] = data['name']
    if 'cc_required' in data:
      update_fields['cc_required'] = data['cc_required']
    if 'account_type' in data:
      update_fields['account_type'] = data['account_type']
    
    # Validate at least one field is being updated
    if not update_fields:
      return app.response_class(response=json.dumps({'message': 'No valid update fields provided'}), status=400, mimetype='application/json')

    with session:
      try:
        update_result = update_account(session, account_id, update_fields)
        return app.response_class(response=json.dumps(update_result), status=200, mimetype='application/json')
      except BadRequest as e:
        return app.response_class(response=json.dumps({'message': str(e)}), status=400, mimetype='application/json')
      except AccountException as e:
        return app.response_class(response=json.dumps({'message': e.__str__()}), status=e.status_code, mimetype='application/json')
      except Exception as e:
        return app.response_class(response=json.dumps({'message': e.__str__()}), status=500, mimetype='application/json')
      
  def delete(self, account_id):
    session = Session()
    with session:
      try:
        result = delete_account(session, account_id)
        return app.response_class(response=json.dumps(result), status=200, mimetype='application/json')
      except BadRequest as e:
        return app.response_class(response=json.dumps({'message': str(e)}), status=400, mimetype='application/json')
      except AccountException as e:
        return app.response_class(response=json.dumps({'message': e.__str__()}), status=e.status_code, mimetype='application/json')
      except Exception as e:
        return app.response_class(response=json.dumps({'message': e.__str__()}), status=500, mimetype='application/json')    

class AccountBalanceResource(Resource):
    def get(self, account_id):
        """Get account balance by ID"""
        session = Session()
        with session:
            try:
                result = get_account_with_balance(session, account_id)
                return app.response_class(
                    response=json.dumps(result),
                    status=200,
                    mimetype='application/json'
                )
            except Exception as e:
                return app.response_class(
                    response=json.dumps({'message': str(e)}),
                    status=500,
                    mimetype='application/json'
                )

class AccountResourceByParentName(Resource):
    def get(self, parent_name):
        session = Session()
        with session:
            try:
                return app.response_class(
                    response=json.dumps(get_accounts_by_parent_name(session, parent_name)),
                    status=200,
                    mimetype='application/json'
                )
            except AccountNotFoundException as e:
                return app.response_class(
                    response=json.dumps({'message': str(e)}),
                    status=404,
                    mimetype='application/json'
                )
            except Exception as e:
                return app.response_class(
                    response=json.dumps({'message': str(e)}),
                    status=500,
                    mimetype='application/json'
                )