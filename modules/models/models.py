from sqlalchemy import Column, Integer, String, ForeignKey, Float, Sequence, Boolean, DateTime, Text, Numeric, Table, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref
from flask import abort
from enum import Enum
import datetime
import uuid
from werkzeug.security import generate_password_hash, check_password_hash

Base = declarative_base()

# Association table for position-permissions (many-to-many)
position_permissions = Table('position_permissions', Base.metadata,
    Column('position_id', Integer, ForeignKey('positions.id'), primary_key=True),
    Column('permission_id', Integer, ForeignKey('permissions.id'), primary_key=True)
)

# Sequences for auto-incrementing fields
asset_code_seq = Sequence('asset_code_seq', start=1, increment=1)


class AssetStatus(str, Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    MAINTENANCE = "MAINTENANCE"
    DISPOSED = "DISPOSED"


class UserStatus(str, Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    SUSPENDED = "SUSPENDED"


class Company(Base):
    __tablename__ = 'company'  # Single company table
    
    id = Column(Integer, primary_key=True, default=1)  # Always ID = 1 for single company
    name_en = Column(String(200), nullable=False)
    name_ar = Column(String(200), nullable=False)
    address_en = Column(Text, nullable=True)
    address_ar = Column(Text, nullable=True)
    phone = Column(String(50), nullable=True)
    email = Column(String(100), nullable=True)
    commercial_registry = Column(String(50), nullable=True)
    tax_number = Column(String(50), nullable=True)
    website = Column(String(200), nullable=True)
    logo_path = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    
    # Relationships
    branches = relationship('Branch', back_populates='company')
    
    @staticmethod
    def get_company():
        """Get the single company instance"""
        from modules.app import Session
        session = Session()
        try:
            company = session.query(Company).first()
            return company
        finally:
            session.close()
    
    def to_dict(self):
        return {
            'id': self.id,
            'name_en': self.name_en,
            'name_ar': self.name_ar,
            'address_en': self.address_en,
            'address_ar': self.address_ar,
            'phone': self.phone,
            'email': self.email,
            'commercial_registry': self.commercial_registry,
            'tax_number': self.tax_number,
            'website': self.website,
            'logo_path': self.logo_path,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class Branch(Base):
    __tablename__ = 'branches'
    
    id = Column(Integer, primary_key=True)
    company_id = Column(Integer, ForeignKey('company.id'), nullable=False, default=1)  # Always company ID = 1
    name_en = Column(String(200), nullable=False)
    name_ar = Column(String(200), nullable=False)
    address_en = Column(Text, nullable=True)
    address_ar = Column(Text, nullable=True)
    phone = Column(String(50), nullable=True)
    email = Column(String(100), nullable=True)
    manager_name = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    is_active = Column(Boolean, default=True)
    
    # Relationships
    company = relationship('Company', back_populates='branches')
    warehouses = relationship('Warehouse', back_populates='branch')
    users = relationship('User', back_populates='branch')
    assets = relationship('Asset', back_populates='branch')
    
    def to_dict(self):
        return {
            'id': self.id,
            'company_id': self.company_id,
            'name_en': self.name_en,
            'name_ar': self.name_ar,
            'address_en': self.address_en,
            'address_ar': self.address_ar,
            'phone': self.phone,
            'email': self.email,
            'manager_name': self.manager_name,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class Warehouse(Base):
    __tablename__ = 'warehouses'
    
    id = Column(Integer, primary_key=True)
    branch_id = Column(Integer, ForeignKey('branches.id'), nullable=False)
    name_en = Column(String(200), nullable=False)
    name_ar = Column(String(200), nullable=False)
    location = Column(Text, nullable=True)
    description = Column(Text, nullable=True)
    capacity = Column(Float, nullable=True)
    manager_name = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    is_active = Column(Boolean, default=True)
    
    # Relationships
    branch = relationship('Branch', back_populates='warehouses')
    assets = relationship('Asset', back_populates='warehouse')
    
    def to_dict(self):
        return {
            'id': self.id,
            'branch_id': self.branch_id,
            'name_en': self.name_en,
            'name_ar': self.name_ar,
            'location': self.location,
            'description': self.description,
            'capacity': self.capacity,
            'manager_name': self.manager_name,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class Position(Base):
    __tablename__ = 'positions'
    
    id = Column(Integer, primary_key=True)
    name_en = Column(String(100), nullable=False, unique=True)
    name_ar = Column(String(100), nullable=False, unique=True)
    description = Column(Text, nullable=True)
    level = Column(Integer, default=1)  # Hierarchy level
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    is_active = Column(Boolean, default=True)
    
    # Relationships
    users = relationship('User', back_populates='position')
    permissions = relationship('Permission', secondary=position_permissions, back_populates='positions')
    
    def to_dict(self):
        return {
            'id': self.id,
            'name_en': self.name_en,
            'name_ar': self.name_ar,
            'description': self.description,
            'level': self.level,
            'is_active': self.is_active,
            'permissions': [perm.to_dict() for perm in self.permissions],
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class Permission(Base):
    __tablename__ = 'permissions'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False, unique=True)
    code = Column(String(50), nullable=False, unique=True)
    description = Column(Text, nullable=True)
    module = Column(String(50), nullable=False)  # company, branch, warehouse, asset, user, report, etc.
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    is_active = Column(Boolean, default=True)
    
    # Relationships - users only get permissions through positions
    positions = relationship('Position', secondary=position_permissions, back_populates='permissions')
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'code': self.code,
            'description': self.description,
            'module': self.module,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    username = Column(String(50), nullable=False, unique=True)
    email = Column(String(100), nullable=False, unique=True)
    password_hash = Column(String(255), nullable=False)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    phone = Column(String(20), nullable=True)
    position_id = Column(Integer, ForeignKey('positions.id'), nullable=False)
    branch_id = Column(Integer, ForeignKey('branches.id'), nullable=False)
    employee_id = Column(String(50), nullable=True, unique=True)
    hire_date = Column(Date, nullable=True)
    status = Column(String(20), default=UserStatus.ACTIVE)
    last_login = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    created_by = Column(Integer, ForeignKey('users.id'), nullable=True)
    
    # Relationships
    position = relationship('Position', back_populates='users')
    branch = relationship('Branch', back_populates='users')
    created_assets = relationship('Asset', back_populates='created_by_user')
    asset_transfers_from = relationship('AssetTransfer', foreign_keys='AssetTransfer.transferred_by', back_populates='transferred_by_user')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def get_all_permissions(self):
        """Get all permissions from position (users don't have individual permissions)"""
        if self.position and self.position.is_active:
            return [perm for perm in self.position.permissions if perm.is_active]
        return []
    
    def has_permission(self, permission_code):
        """Check if user has permission through their position"""
        if not self.position or not self.position.is_active:
            return False
        
        # Check position permissions
        for perm in self.position.permissions:
            if perm.code == permission_code and perm.is_active:
                return True
        
        return False
    
    def change_position(self, new_position_id):
        """Change user position - automatically updates all permissions"""
        self.position_id = new_position_id
        self.updated_at = datetime.datetime.utcnow()
        # Permissions are automatically inherited from the new position
    
    def to_dict(self, include_permissions=False):
        user_dict = {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'phone': self.phone,
            'employee_id': self.employee_id,
            'hire_date': self.hire_date.isoformat() if self.hire_date else None,
            'status': self.status,
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'position': self.position.to_dict() if self.position else None,
            'branch': self.branch.to_dict() if self.branch else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
        
        if include_permissions:
            user_dict['permissions'] = [perm.to_dict() for perm in self.get_all_permissions()]
        
        return user_dict


class AssetCategory(Base):
    __tablename__ = 'asset_categories'
    
    id = Column(Integer, primary_key=True)
    name_en = Column(String(100), nullable=False, unique=True)
    name_ar = Column(String(100), nullable=False, unique=True)
    code = Column(String(20), nullable=False, unique=True)
    description = Column(Text, nullable=True)
    parent_id = Column(Integer, ForeignKey('asset_categories.id'), nullable=True)
    depreciation_rate = Column(Float, nullable=True)  # Annual depreciation rate
    useful_life_years = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    is_active = Column(Boolean, default=True)
    
    # Relationships
    parent = relationship("AssetCategory", remote_side=[id], backref=backref('children'))
    assets = relationship('Asset', back_populates='category')
    
    def to_dict(self):
        return {
            'id': self.id,
            'name_en': self.name_en,
            'name_ar': self.name_ar,
            'code': self.code,
            'description': self.description,
            'parent_id': self.parent_id,
            'depreciation_rate': self.depreciation_rate,
            'useful_life_years': self.useful_life_years,
            'is_active': self.is_active,
            'children': [child.to_dict() for child in self.children],
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class Asset(Base):
    __tablename__ = 'assets'
    
    id = Column(Integer, primary_key=True)
    asset_code = Column(String(50), nullable=False, unique=True)
    name_en = Column(String(200), nullable=False)
    name_ar = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    category_id = Column(Integer, ForeignKey('asset_categories.id'), nullable=False)
    branch_id = Column(Integer, ForeignKey('branches.id'), nullable=False)
    warehouse_id = Column(Integer, ForeignKey('warehouses.id'), nullable=False)
    
    # Purchase Information
    purchase_date = Column(Date, nullable=False)
    purchase_value = Column(Numeric(15, 2), nullable=False)
    invoice_number = Column(String(100), nullable=True)
    supplier_name = Column(String(200), nullable=True)
    warranty_start_date = Column(Date, nullable=True)
    warranty_end_date = Column(Date, nullable=True)
    
    # Physical Information
    quantity = Column(Integer, default=1)
    unit = Column(String(20), nullable=True)
    serial_number = Column(String(100), nullable=True)
    model = Column(String(100), nullable=True)
    manufacturer = Column(String(100), nullable=True)
    
    # Current Information
    current_value = Column(Numeric(15, 2), nullable=True)
    accumulated_depreciation = Column(Numeric(15, 2), default=0)
    status = Column(String(20), default=AssetStatus.ACTIVE)
    location_notes = Column(Text, nullable=True)
    
    # Barcode and Tracking
    barcode = Column(String(100), nullable=True, unique=True)
    qr_code = Column(String(500), nullable=True)
    rfid_tag = Column(String(100), nullable=True)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    created_by = Column(Integer, ForeignKey('users.id'), nullable=False)
    last_maintenance_date = Column(Date, nullable=True)
    next_maintenance_date = Column(Date, nullable=True)
    
    # Relationships
    category = relationship('AssetCategory', back_populates='assets')
    branch = relationship('Branch', back_populates='assets')
    warehouse = relationship('Warehouse', back_populates='assets')
    created_by_user = relationship('User', back_populates='created_assets')
    attachments = relationship('AssetAttachment', back_populates='asset')
    transfers = relationship('AssetTransfer', back_populates='asset')
    maintenance_records = relationship('AssetMaintenance', back_populates='asset')
    
    def calculate_depreciation(self):
        """Calculate current depreciation based on category settings"""
        if not self.category or not self.category.depreciation_rate:
            return 0
        
        years_since_purchase = (datetime.date.today() - self.purchase_date).days / 365.25
        annual_depreciation = float(self.purchase_value) * (self.category.depreciation_rate / 100)
        return annual_depreciation * years_since_purchase
    
    def get_current_book_value(self):
        """Calculate current book value"""
        return float(self.purchase_value) - float(self.accumulated_depreciation or 0)
    
    def to_dict(self, include_relations=True):
        asset_dict = {
            'id': self.id,
            'asset_code': self.asset_code,
            'name_en': self.name_en,
            'name_ar': self.name_ar,
            'description': self.description,
            'purchase_date': self.purchase_date.isoformat() if self.purchase_date else None,
            'purchase_value': float(self.purchase_value),
            'invoice_number': self.invoice_number,
            'supplier_name': self.supplier_name,
            'warranty_start_date': self.warranty_start_date.isoformat() if self.warranty_start_date else None,
            'warranty_end_date': self.warranty_end_date.isoformat() if self.warranty_end_date else None,
            'quantity': self.quantity,
            'unit': self.unit,
            'serial_number': self.serial_number,
            'model': self.model,
            'manufacturer': self.manufacturer,
            'current_value': float(self.current_value) if self.current_value else None,
            'accumulated_depreciation': float(self.accumulated_depreciation),
            'book_value': self.get_current_book_value(),
            'status': self.status,
            'location_notes': self.location_notes,
            'barcode': self.barcode,
            'qr_code': self.qr_code,
            'rfid_tag': self.rfid_tag,
            'last_maintenance_date': self.last_maintenance_date.isoformat() if self.last_maintenance_date else None,
            'next_maintenance_date': self.next_maintenance_date.isoformat() if self.next_maintenance_date else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
        
        if include_relations:
            asset_dict.update({
                'category': self.category.to_dict() if self.category else None,
                'branch': self.branch.to_dict() if self.branch else None,
                'warehouse': self.warehouse.to_dict() if self.warehouse else None,
                'created_by': self.created_by_user.to_dict() if self.created_by_user else None,
                'attachments': [att.to_dict() for att in self.attachments]
            })
        
        return asset_dict


class AssetAttachment(Base):
    __tablename__ = 'asset_attachments'
    
    id = Column(Integer, primary_key=True)
    asset_id = Column(Integer, ForeignKey('assets.id'), nullable=False)
    file_name = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_type = Column(String(50), nullable=False)
    file_size = Column(Integer, nullable=False)  # in bytes
    description = Column(Text, nullable=True)
    uploaded_by = Column(Integer, ForeignKey('users.id'), nullable=False)
    uploaded_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    # Relationships
    asset = relationship('Asset', back_populates='attachments')
    uploader = relationship('User')
    
    def to_dict(self):
        return {
            'id': self.id,
            'asset_id': self.asset_id,
            'file_name': self.file_name,
            'file_path': self.file_path,
            'file_type': self.file_type,
            'file_size': self.file_size,
            'description': self.description,
            'uploaded_by': self.uploader.to_dict() if self.uploader else None,
            'uploaded_at': self.uploaded_at.isoformat() if self.uploaded_at else None
        }


class AssetTransfer(Base):
    __tablename__ = 'asset_transfers'
    
    id = Column(Integer, primary_key=True)
    asset_id = Column(Integer, ForeignKey('assets.id'), nullable=False)
    from_branch_id = Column(Integer, ForeignKey('branches.id'), nullable=True)
    to_branch_id = Column(Integer, ForeignKey('branches.id'), nullable=True)
    from_warehouse_id = Column(Integer, ForeignKey('warehouses.id'), nullable=True)
    to_warehouse_id = Column(Integer, ForeignKey('warehouses.id'), nullable=True)
    transfer_date = Column(DateTime, default=datetime.datetime.utcnow)
    reason = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)
    transferred_by = Column(Integer, ForeignKey('users.id'), nullable=False)
    approved_by = Column(Integer, ForeignKey('users.id'), nullable=True)
    status = Column(String(20), default='PENDING')  # PENDING, APPROVED, REJECTED, COMPLETED
    
    # Relationships
    asset = relationship('Asset', back_populates='transfers')
    from_branch = relationship('Branch', foreign_keys=[from_branch_id])
    to_branch = relationship('Branch', foreign_keys=[to_branch_id])
    from_warehouse = relationship('Warehouse', foreign_keys=[from_warehouse_id])
    to_warehouse = relationship('Warehouse', foreign_keys=[to_warehouse_id])
    transferred_by_user = relationship('User', foreign_keys=[transferred_by], back_populates='asset_transfers_from')
    approved_by_user = relationship('User', foreign_keys=[approved_by])
    
    def to_dict(self):
        return {
            'id': self.id,
            'asset': self.asset.to_dict(include_relations=False) if self.asset else None,
            'from_branch': self.from_branch.to_dict() if self.from_branch else None,
            'to_branch': self.to_branch.to_dict() if self.to_branch else None,
            'from_warehouse': self.from_warehouse.to_dict() if self.from_warehouse else None,
            'to_warehouse': self.to_warehouse.to_dict() if self.to_warehouse else None,
            'transfer_date': self.transfer_date.isoformat() if self.transfer_date else None,
            'reason': self.reason,
            'notes': self.notes,
            'transferred_by': self.transferred_by_user.to_dict() if self.transferred_by_user else None,
            'approved_by': self.approved_by_user.to_dict() if self.approved_by_user else None,
            'status': self.status
        }


class AssetMaintenance(Base):
    __tablename__ = 'asset_maintenance'
    
    id = Column(Integer, primary_key=True)
    asset_id = Column(Integer, ForeignKey('assets.id'), nullable=False)
    maintenance_type = Column(String(50), nullable=False)  # PREVENTIVE, CORRECTIVE, EMERGENCY
    description = Column(Text, nullable=False)
    maintenance_date = Column(Date, nullable=False)
    cost = Column(Numeric(10, 2), nullable=True)
    supplier_name = Column(String(200), nullable=True)
    performed_by = Column(String(200), nullable=True)
    next_maintenance_date = Column(Date, nullable=True)
    status = Column(String(20), default='COMPLETED')  # SCHEDULED, IN_PROGRESS, COMPLETED, CANCELLED
    notes = Column(Text, nullable=True)
    created_by = Column(Integer, ForeignKey('users.id'), nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    # Relationships
    asset = relationship('Asset', back_populates='maintenance_records')
    creator = relationship('User')
    
    def to_dict(self):
        return {
            'id': self.id,
            'asset_id': self.asset_id,
            'maintenance_type': self.maintenance_type,
            'description': self.description,
            'maintenance_date': self.maintenance_date.isoformat() if self.maintenance_date else None,
            'cost': float(self.cost) if self.cost else None,
            'supplier_name': self.supplier_name,
            'performed_by': self.performed_by,
            'next_maintenance_date': self.next_maintenance_date.isoformat() if self.next_maintenance_date else None,
            'status': self.status,
            'notes': self.notes,
            'created_by': self.creator.to_dict() if self.creator else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class AuditLog(Base):
    __tablename__ = 'audit_logs'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    table_name = Column(String(100), nullable=False)
    record_id = Column(Integer, nullable=False)
    action = Column(String(20), nullable=False)  # CREATE, UPDATE, DELETE
    old_values = Column(Text, nullable=True)  # JSON string
    new_values = Column(Text, nullable=True)  # JSON string
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)
    
    # Relationships
    user = relationship('User')
    
    def to_dict(self):
        return {
            'id': self.id,
            'user': self.user.to_dict() if self.user else None,
            'table_name': self.table_name,
            'record_id': self.record_id,
            'action': self.action,
            'old_values': self.old_values,
            'new_values': self.new_values,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'ip_address': self.ip_address,
            'user_agent': self.user_agent
        }


class SystemSettings(Base):
    __tablename__ = 'system_settings'
    
    id = Column(Integer, primary_key=True)
    key = Column(String(100), nullable=False, unique=True)
    value = Column(Text, nullable=False)
    description = Column(Text, nullable=True)
    data_type = Column(String(20), default='string')  # string, integer, float, boolean, json
    updated_by = Column(Integer, ForeignKey('users.id'), nullable=True)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    
    # Relationships
    updater = relationship('User')
    
    def to_dict(self):
        return {
            'id': self.id,
            'key': self.key,
            'value': self.value,
            'description': self.description,
            'data_type': self.data_type,
            'updated_by': self.updater.to_dict() if self.updater else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }