import requests
import json
import os

import email, smtplib, ssl

from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

#KEY HAS BEEN REMOVED FOR SECURITY PURPOSES
order_headers = {
    'NETOAPI_ACTION': "GetOrder",
    'Accept': "application/json",
    'Content-Type': "application/javascript",
    'cache-control': "no-cache",
    'Postman-Token': "2473156a-3bcc-4a64-8079-04c3a395b5ea"
}

product_headers = {
    'NETOAPI_ACTION': "GetItem",
    'Accept': "application/json",
    'Content-Type': "application/javascript",
    'cache-control': "no-cache",
    'Postman-Token': "2473156a-3bcc-4a64-8079-04c3a395b5ea"
}

url = "https://www.findsports.com.au/do/WS/NetoAPI"


def api_order_response(dict_filter, List_of_OutputSelector, new_headers=None):
    parent_dict = {}
    dict_export_status = {}
    if List_of_OutputSelector is None:

        if (new_headers is None):
            temp_list_of_output_selector = [
                "ShippingOption",
                "DeliveryInstruction",
                "Username",
                "Email",
                "ShipAddress",
                "BillAddress",
                "CustomerRef1",
                "CustomerRef2",
                "CustomerRef3",
                "CustomerRef4",
                "SalesChannel",
                "GrandTotal",
                "ShippingTracking",
                "ShippingTotal",
                "ShippingDiscount",
                "OrderType",
                "OrderStatus",
                "OrderPayment",
                "OrderPayment.DatePaid",
                "DatePlaced",
                "InternalOrderNotes",
                "DateRequired",
                "DateInvoiced",
                "DateUpdated",
                "DatePaid",
                "OrderLine",
                "OrderLine.ProductName",
                "OrderLine.PickQuantity",
                "OrderLine.BackorderQuantity",
                "OrderLine.UnitPrice",
                "OrderLine.WarehouseID",
                "OrderLine.WarehouseName",
                "OrderLine.WarehouseReference",
                "OrderLine.Quantity",
                "OrderLine.PercentDiscount",
                "OrderLine.ProductDiscount",
                "OrderLine.CostPrice",
                "OrderLine.ShippingMethod",
                "OrderLine.ShippingTracking",
                "ShippingSignature",
                "eBay.eBayUsername",
                "eBay.eBayStoreName",
                "OrderLine.eBay.eBayTransactionID",
                "OrderLine.eBay.eBayAuctionID",
                "OrderLine.eBay.ListingType",
                "OrderLine.eBay.DateCreated",
                "OrderLine.eBay.DatePaid"
            ]
        else:
            temp_list_of_output_selector = ["OrderID", "InvoiceNumber", "CustomerUsername", "StaffUsername",
                                            "PurchaseOrderNumber", "InternalNotes", "CurrencyCode", "RmaStatus",
                                            "ShippingRefundAmount", "ShippingRefundTaxCode",
                                            "SurchargeRefundAmount",
                                            "RefundSubtotal", "RefundTotal", "RefundTaxTotal", "TaxInclusive",
                                            "DateIssued", "DateUpdated", "DateApproved", "RmaLine",
                                            "RmaLine.ItemNumber", "RmaLine.Extra", "RmaLine.ExtraOptions",
                                            "RmaLine.ItemNotes", "RmaLine.ProductName", "RmaLine.RefundSubtotal",
                                            "RmaLine.Tax", "RmaLine.TaxCode", "RmaLine.WarehouseID",
                                            "RmaLine.WarehouseName", "RmaLine.WarehouseReference",
                                            "RmaLine.ResolutionOutcome", "RmaLine.ReturnReason",
                                            "RmaLine.ItemStatusType", "RmaLine.ItemStatus",
                                            "RmaLine.ResolutionStatus",
                                            "RmaLine.ManufacturerClaims", "RmaLine.IsRestockIssued",
                                            "RefundedTotal","SKU",
                                            "Refund", "Refund.PaymentMethodID", "Refund.PaymentMethodName",
                                            "Refund.DateIssued", "Refund.DateRefunded", "Refund.RefundStatus"]

        dict_filter["OutputSelector"] = temp_list_of_output_selector
    else:
        dict_filter['OutputSelector'] = List_of_OutputSelector

    dict_export_status["ExportStatus"] = "Exported"
    dict_filter["UpdateResults"] = dict_export_status

    parent_dict['Filter'] = dict_filter

    payload = json.dumps(parent_dict)

    if (new_headers is None):
        header = order_headers

    response = requests.request("POST", url, data=payload, headers=header)

    json1_data = json.loads(response.text)

    return json1_data

def api_product_response(dict_filter, List_of_OutputSelector=None, new_headers=None):
    parent_dict = {}
    dict_export_status = {}
    if List_of_OutputSelector is None:

        if (new_headers is None):
            temp_list_of_output_selector = [
                "SKU", "ParentSKU", "ID", "Brand", "Model", "Virtual", "Name", "PrimarySupplier", "Approved",
                "IsActive",
                "IsNetoUtility", "AuGstExempt", "NzGstExempt", "IsGiftVoucher", "FreeGifts", "CrossSellProducts",
                "UpsellProducts", "PriceGroups", "ItemLength", "ItemWidth", "ItemHeight", "ShippingLength",
                "ShippingWidth", "ShippingHeight", "ShippingWeight", "CubicWeight", "HandlingTime",
                "WarehouseQuantity",
                "WarehouseLocations", "CommittedQuantity", "AvailableSellQuantity", "ItemSpecifics", "Categories",
                "AccountingCode", "SortOrder1", "SortOrder2", "RRP", "DefaultPrice", "PromotionPrice",
                "PromotionStartDate", "PromotionStartDateLocal", "PromotionStartDateUTC", "PromotionExpiryDate",
                "PromotionExpiryDateLocal", "PromotionExpiryDateUTC", "DateArrival", "DateArrivalUTC", "CostPrice",
                "UnitOfMeasure", "BaseUnitOfMeasure", "BaseUnitPerQuantity", "QuantityPerScan", "BuyUnitQuantity",
                "SellUnitQuantity", "PreOrderQuantity", "PickPriority", "PickZone", "eBayProductIDs", "TaxCategory",
                "TaxFreeItem", "TaxInclusive", "SearchKeywords", "ShortDescription", "Description", "Features",
                "Specifications", "Warranty", "eBayDescription", "TermsAndConditions", "ArtistOrAuthor", "Format",
                "ModelNumber", "Subtitle", "AvailabilityDescription", "Images", "ImageURL", "BrochureURL",
                "ProductURL",
                "DateAdded", "DateAddedLocal", "DateAddedUTC", "DateCreatedLocal", "DateCreatedUTC", "DateUpdated",
                "DateUpdatedLocal", "DateUpdatedUTC", "UPC", "UPC1", "UPC2", "UPC3", "Type", "SubType",
                "NumbersOfLabelsToPrint", "ReferenceNumber", "InternalNotes", "BarcodeHeight", "SupplierItemCode",
                "SplitForWarehousePicking", "DisplayTemplate", "EditableKitBundle", "RequiresPackaging", "IsAsset",
                "WhenToRepeatOnStandingOrders", "SerialTracking", "Group", "ShippingCategory",
                "MonthlySpendRequirement", "RestrictedToUserGroup", "IsInventoried", "IsBought", "IsSold",
                "ExpenseAccount", "PurchaseTaxCode", "CostOfSalesAccount", "IncomeAccount", "AssetAccount",
                "KitComponents", "SEOPageTitle", "SEOMetaKeywords", "SEOPageHeading", "SEOMetaDescription",
                "SEOCanonicalURL", "ItemURL", "AutomaticURL", "Job", "RelatedContents", "SalesChannels", "Misc01",
                "Misc02", "Misc03", "Misc04", "Misc05", "Misc06", "Misc07", "Misc08", "Misc09", "Misc10", "Misc11",
                "Misc12", "Misc13", "Misc14", "Misc15", "Misc16", "Misc17", "Misc18", "Misc19", "Misc20", "Misc21",
                "Misc22", "Misc23", "Misc24", "Misc25", "Misc26", "Misc27", "Misc28", "Misc29", "Misc30", "Misc31",
                "Misc32", "Misc33", "Misc34", "Misc35", "Misc36", "Misc37", "Misc38", "Misc39", "Misc40", "Misc41",
                "Misc42", "Misc43", "Misc44", "Misc45", "Misc46", "Misc47", "Misc48", "Misc49", "Misc50", "Misc51",
                "Misc52"
            ]

        dict_filter["OutputSelector"] = temp_list_of_output_selector
    else:
        dict_filter['OutputSelector'] = List_of_OutputSelector

    dict_export_status["ExportStatus"] = "Exported"
    dict_filter["UpdateResults"] = dict_export_status

    parent_dict['Filter'] = dict_filter

    payload = json.dumps(parent_dict)

    if new_headers is None:
        header = product_headers
    # else:
    #     header = rma_headers

    response = requests.request("POST", url, data=payload, headers=header)

    json1_data = json.loads(response.text)

    return json1_data








def sendemailofficial(subject, body, receiver_email, path_to_attachment,actualfilename=None, attachment=False):
    # CREDENTIALS HAVE BEEN REMOVED FOR SECURITY PURPOSES
    sender_email = ""
    password = ''

    # Create a multipart message and set headers
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = subject
    #message["Bcc"] = receiver_email  # Recommended for mass emails

    # Add body to email
    message.attach(MIMEText(body))

    if (attachment):
        filename = path_to_attachment  # In same directory as script

        # Open PDF file in binary mode
        with open(filename, "rb") as attachment:
            # Add file as application/octet-stream
            # Email client can usually download this automatically as attachment
            part = MIMEBase("application", "octet-stream")
            part.set_payload(attachment.read())

        # Encode file in ASCII characters to send by email
        encoders.encode_base64(part)


        if not(actualfilename==None):
            filename=actualfilename

        # Add header as key/value pair to attachment part
        part.add_header(
            "Content-Disposition",
            f"attachment; filename= {filename}",
        )

        # Add attachment to message and convert message to string
        message.attach(part)
    text = message.as_string()

    # Log in to server using secure context and send email
    context = ssl.create_default_context()

    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, text)


def sendemail(subject, body, receiver_email, path_to_attachment,actualfilename=None, attachment=False,cc=[""]):
    # CREDENTIALS HAVE BEEN REMOVED FOR SECURITY PURPOSES
    sender_email = ""
    password = ''
    cc = ",".join(cc)
    print(cc)

    # Create a multipart message and set headers
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = subject
    message["CC"] = cc  # Recommended for mass emails

    # Add body to email
    message.attach(MIMEText(body, "html"))

    if (attachment):
        filename = path_to_attachment  # In same directory as script

        # Open PDF file in binary mode
        with open(filename, "rb") as attachment:
            # Add file as application/octet-stream
            # Email client can usually download this automatically as attachment
            part = MIMEBase("application", "octet-stream")
            part.set_payload(attachment.read())

        # Encode file in ASCII characters to send by email
        encoders.encode_base64(part)


        if not(actualfilename==None):
            filename=actualfilename

        # Add header as key/value pair to attachment part
        part.add_header(
            "Content-Disposition",
            f"attachment; filename= {filename}",
        )

        # Add attachment to message and convert message to string
        message.attach(part)
    text = message.as_string()

    # Log in to server using secure context and send email
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, text)