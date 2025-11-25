# -*- coding: utf-8 -*-
"""
Created on Mon Nov 17 19:17:34 2025

@author: brendan

This module outlines the database tables

"""
# %% Global imports
from collections.abc import Callable
from datetime import date, datetime
from decimal import Decimal
from sqlalchemy import ( 
    Boolean,
    Column, 
    CheckConstraint,
    Date,
    DateTime,
    Float, 
    ForeignKey, 
    Integer, 
    Numeric,
    String,
    )
from sqlalchemy.orm import ( 
    DeclarativeBase, 
    Mapped, 
    mapped_column, 
    sessionmaker,
    )

import pyjson5

# %% py_contractor_uk imports
from py_contractor.config.config import Config


# %% Module level configuration

# declarative base class
class Base(DeclarativeBase):
    pass


# %% Classes (objects)


# -----------------------------------------------------------------------------
class BankAccount(Base):
    """!
    A bank account of the contractor firm
    
    """
    
    __tablename__ = "bank_accounts"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    
    contractor_company_id: Mapped[int] = mapped_column(
        ForeignKey("ContractorCompany.id"),
        comment="The id of the contracting company associated to this bank "
        "account"
        )
    bank_name: Mapped[str] = mapped_column(
        String,
        comment="The name of the bank, i.e. Ulster Bank",
        )
    
    branch_address: Mapped[str] = mapped_column(
        String,
        comment="The address of the branch the account is registered at"
        )
    
    interest_rate: Mapped[float] = mapped_column(
        Float,
        comment="The annual interest rate (%)",
        )
    
    account_type: Mapped[str] = mapped_column(
        String,
        comment="Type of account, i.e. 'current', 'credit card', 'savings'",
        )  # May make this an enum type later
    
    banking_fees_mnth: Mapped[float] = mapped_column(
        Float,
        comment="The _monthly_ fees for holding this account")
    
    current_balance: Mapped[float] = mapped_column(
        Float,
        comment="The current balance of the account")
    
    sort_code: Mapped[str] = mapped_column(
        String,
        comment="The account sort code - salted+hashed",
        )
    account_number: Mapped[str] = mapped_column(
        String,
        comment="The account number - salted+hashed",
        )
    iban_number: Mapped[str] = mapped_column(
        String,
        comment="The IBAN number - salted+hashed",
        )


# -----------------------------------------------------------------------------
class BankAccountTransaction:
    """!
    **For holding a record of transactions into and out of bank accounts**
    
    """
    
    __tablename__ = "bank_account_transactions"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    
    account_id: Mapped[int] = mapped_column(
        ForeignKey("BankAccount.id"),
        )
    
    transaction_datetime: Mapped[datetime] = mapped_column(
        DateTime,
        comment="The datetime of the transaction"
        )
    
    client_id: Mapped[int] = mapped_column(
        ForeignKey("Client.id"),
        nullable=True,
        )
    
    supplier_id: Mapped[int] = mapped_column(
        ForeignKey("Supplier.id"),
        nullable=True,
        )


# -----------------------------------------------------------------------------
class Client(Base):
    """!
    A client of the contractor
    
    """
    
    __tablename__ = "clients"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    
    contractor_company_id: Mapped[int] = mapped_column(
        ForeignKey("ContractorCompany.id"),
        comment="The identifier of the contractor company associated to this "
        "client, there may be multiple rows of same client for different "
        "contracting companies."
        )
    
    name: Mapped[str] = mapped_column(
        String,
        comment="The nominal name of the client",
        )
    
    billing_address: Mapped[str] = mapped_column(
        String,
        comment="The address that invoicing etc should be addressed to",
        )
    
    billing_contact_email: Mapped[str] = mapped_column(
        String,
        comment="The contact email for the client - for billing",
        )
    
    vat_id: Mapped[str] = mapped_column(
        String,
        comment="The VAT ID of the client. Not sure if this needs hashed or "
        "not")
    
    
# -----------------------------------------------------------------------------
class Contract(Base):
    """!
    A contract between the contractor and the client
    
    """
    
    __tablename__ = "contracts"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    
    client_id: Mapped[int] = mapped_column(
        ForeignKey("Client.id"),
        )
    
    contractor_company_id: Mapped[int] = mapped_column(
        ForeignKey("ContractorCompany.id"),
        )
    
    start_date: Mapped[date] = mapped_column(
        Date,
        )
    
    end_date: Mapped[date] = mapped_column(
        Date,
        )
    
    hourly_rate: Mapped[float] = mapped_column(
        Float,
        comment="The base hourly rate, excluding VAT",
        )


# -----------------------------------------------------------------------------
class ContractorCompany:
    """!
    The contracting company
    
    Holding this in a table would enable two modes:
        - single user operation, i.e. the contractor themselves
        - accountant representing several contractors
        
    """
    
    __tablename__ = "contractor_companies"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    
    name: Mapped[str] = mapped_column(
        String,
        comment="The nominal name of the contracting company",
        )
    
    registered_address: Mapped[str] = mapped_column(
        String,
        comment="The registered address of the contracting company",
        )
    postal_address: Mapped[str] = mapped_column(
        String,
        comment="The postal address of the contracting company",
        )
    email_address: Mapped[str] = mapped_column(
        String,
        comment="The nominal email address of the contracting company",
        )
    
    director_name: Mapped[str] = mapped_column(
        String,
        comment="Name of the director of the company",
        )
    director_address: Mapped[str] = mapped_column(
        String,
        comment="The contact address of the director of the contracting "
        "company",
        )
    director_phone: Mapped[str] = mapped_column(
        String,
        comment="The phone number of the director of the contracting company",
        )
    director_email: Mapped[str] = mapped_column(
        String,
        comment="The email of the director of the contracting company",
        )
    
    vat_registration_number: Mapped[str] = mapped_column(
        String,
        comment="The vat registration number (VRN) of the contracting company,"
        " leave empty if not VAT registered",
        nullable=True,
        )
    company_number: Mapped[str] = mapped_column(
        String,
        comment="The company number of the contracting company as registered "
        "with companies house",
        )
    utr_number: Mapped[str] = mapped_column(
        String,
        comment="The UTR of the contracting company",
        )  # Is this a thing? Or am I getting mixed up with personal tax
    
    
# -----------------------------------------------------------------------------
class ContractorCompanyPerson:
    """!
    Persons within a contracting company
    
    Holding this in a table would enable two modes:
        - single user operation, i.e. the contractor themselves
        - accountant representing several contractors
        
    """
    
    __tablename__ = "contractor_company_personnel"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    
    contractor_company_id: Mapped[int] = mapped_column(
        ForeignKey("ContractorCompany.id"),
        comment="The id of the contracting company associated to this person"
        )
    
    forename: Mapped[str] = mapped_column(
        String,
        comment="The forename of the person",
        )
    surname: Mapped[str] = mapped_column(
        String,
        comment="The surname name of the person",
        )
    
    address: Mapped[str] = mapped_column(
        String,
        comment="The address of the person",
        )
    postcode: Mapped[str] = mapped_column(
        String,
        comment="The postcode of the person",
        )
    postal_town: Mapped[str] = mapped_column(
        String,
        comment="The postal town of the person",
        )
    
    phone_number: Mapped[str] = mapped_column(
        String,
        comment="The phone number of the person",
        )
    email_address: Mapped[str] = mapped_column(
        String,
        comment="The email of the person",
        )
    
    taxman_utr: Mapped[str] = mapped_column(
        String,
        comment="The UTR number of the person (hashed+salted)",
        )
    
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        comment="Whether the client is active",
        )
    
# -----------------------------------------------------------------------------
class Supplier(Base):
    """!
    A supplier of goods/services to the contractor
    
    """
    
    __tablename__ = "suppliers"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    
    contractor_company_id: Mapped[int] = mapped_column(
        ForeignKey("ContractorCompany.id"),
        comment="The id of the contracting company associated to this supplier"
        )
    
    name: Mapped[str] = mapped_column(
        String,
        comment="The nominal name of the client",
        )
    
    billing_address: Mapped[str] = mapped_column(
        String,
        comment="The address that invoicing etc should be addressed to",
        )
    
    billing_contact_email: Mapped[str] = mapped_column(
        String,
        comment="The contact email for the client - for billing",
        )
    
    vat_id: Mapped[str] = mapped_column(
        String,
        comment="The VAT ID of the client. Not sure if this needs hashed or "
        "not")
    

# -----------------------------------------------------------------------------    
class TaxMan(Base):
    """!
    Holdings of settings for the taxman (HMRC)
    
    This should be generic across contracting companies
    
    """
    
    __tablename__ = "tax_man"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    
    financial_year: Mapped[str] = mapped_column(
        String,
        comment="The year for which this taxman setting applies")
    
    tax: Mapped[str] = mapped_column(
        String,
        comment="The name of the tax, i.e. 'corporation', 'vat', 'income'",
        )  # Will likely change this to an enum
    
    rate_pc: Mapped[float] = mapped_column(
        Float,
        comment="The rate of tax (minimum rate if there is a ramp)",
        )
    
    min_threshold: Mapped[float] = mapped_column(
        Float,
        comment="The minimum threshold at which the tax applies",
        )
    
    max_rate_pc: Mapped[float] = mapped_column(
        Float,
        nullable=True,
        comment="The maximum rate of tax (if there is a ramp)",
        )
    
    ramp_rate: Mapped[float] = mapped_column(
        Float,
        nullable=True,
        comment="The ramp rate (if there is a ramp)",
        )
    
    # Need to think about this, as it gets difficult with banding.
    
# -----------------------------------------------------------------------------    
class TaxManVatSubmissions(Base):
    """!
    Record of preliminary and final VAT submissions to taxman
    
    """
    
    __tablename__ = "tax_man_vat_submissions"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    
    contractor_company_id: Mapped[int] = mapped_column(
        ForeignKey("ContractorCompany.id"),
        comment="The id of the contracting company associated to this supplier"
        )
    
    quarter_end_date: Mapped[date] = mapped_column(
        Date,
        comment="The end date of the VAT quarter of this submission"
        )
    
    datetime_submitted: Mapped[datetime] = mapped_column(
        DateTime,
        comment="The datetime of the submission to HMRC"
        )
    
    # These are pulled from hmrc mtd
    # https://developer.service.hmrc.gov.uk/api-documentation/docs/api/service/
    # vat-api/1.0/oas/page#tag/organisations/operation/SubmitVATreturnforperiod
    period_key: Mapped[str] = mapped_column(
        String,
        comment="The 'periodKey' on HMRC MTD API, will be 4 chars")
    
    vat_due_on_sales: Mapped[float] = mapped_column(
        Numeric(10, 2),
        comment="The VAT due on sales, vatDueSales key on HMRC MTD API, can "
        "only be to 2 decimal places")
    
    vat_due_on_acquisitions: Mapped[float] = mapped_column(
        Numeric(10, 2),
        comment="The VAT due on acquisitions, vatDueAcquisitions key on HMRC "
        "MTD API, will be a negative if any acquisitions, can only be to 2 "
        "decimal places")
    
    total_vat_due: Mapped[float] = mapped_column(
        Numeric(10, 2),
        comment="The total VAT due for this period, the sum of sales "
        "+ acquisitions, can only be to 2 decimal places")
    
    reclaimed_vat_curr_period: Mapped[float] = mapped_column(
        Numeric(10, 2),
        comment="The amount of VAT reclaimed in the current period, can only "
        "be to 2 decimal places")
    
    net_vat_due: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        CheckConstraint("price >= 0", 
                        name="price_positive"),
        comment="The net value due for current period, the absolute difference"
        " between total_vat_due and reclaimed_vat_curr_period, can only be to "
        "2 decimal places")
    
    total_sales_value_ex_vat: Mapped[float] = mapped_column(
        Numeric(10, 2),
        CheckConstraint("amount >= 0 AND MOD(amount, 1) = 0", 
                        name="amount_is_integer"),
        comment="The total sales for period, excluding VAT, to 2 decimal "
        "places, but both values 0, i.e. 123.00"
        )
    total_purchases_value_ex_vat: Mapped[float] = mapped_column(
        Numeric(10, 2),
        CheckConstraint("amount >= 0 AND MOD(amount, 1) = 0", 
                        name="amount_is_integer"),
        comment="The total purchases for period, excluding VAT, to 2 decimal "
        "places, but both values 0, i.e. 123.00"
        )
    total_goods_supplied_value_ex_vat: Mapped[float] = mapped_column(
        Numeric(10, 2),
        CheckConstraint("amount >= 0 AND MOD(amount, 1) = 0", 
                        name="amount_is_integer"),
        comment="The total goods supplied for period, excluding VAT, to 2 "
        "decimal places, but both values 0, i.e. 123.00"
        )
    total_acquisitions_ex_vat: Mapped[float] = mapped_column(
        Numeric(10, 2),
        CheckConstraint("amount >= 0 AND MOD(amount, 1) = 0", 
                        name="amount_is_integer"),
        comment="The total acquisitions for period, excluding VAT, to 2 "
        "decimal places, but both values 0, i.e. 123.00"
        )
    finalised: Mapped[bool] = mapped_column(
        Boolean,
        comment="True if finalised, False otherwise, if not finalised, then "
        "HMRC considers it an invalid submission and will return a 403 code",
        )