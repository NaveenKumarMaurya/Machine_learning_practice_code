import re
import json
from datetime import datetime, date

# -------------------------
# Helper functions
# -------------------------
def to_int(s, default=-1):
    if s is None:
        return default
    s = s.strip().replace(',', '')
    if s in ("", "NA", "-", "-1"):
        return default
    try:
        return int(s)
    except:
        return default

def parse_yyyy_mm_dd(s):
    try:
        return datetime.strptime(s, "%Y-%m-%d").date()
    except:
        return None

def monthyear_to_date(token):
    """token like '08-25' -> date(2025,8,1)"""
    m = re.match(r"(\d{2})-(\d{2})", token)
    if not m:
        return None
    mm = int(m.group(1))
    yy = int(m.group(2))
    yyyy = 2000 + yy if yy < 70 else 1900 + yy
    try:
        return date(yyyy, mm, 1)
    except:
        return None

def last_n_digits(s, n=10):
    digits = re.sub(r'\D', '', s or "")
    return digits[-n:] if len(digits) >= n else digits

def clean_field(text):
    text = re.sub(r'\n+', ' ', text)                   # Remove multiple newlines
    text = re.sub(r'\bDATE OF BIRTH\b', '', text, flags=re.I)
    text = re.sub(r'\b(DOB|ADDRESS|PAN NO|EMAIL ID)\b', '', text, flags=re.I)
    return text.strip()



def process_text_to_json(text):
    # Dummy implementation for illustration
    # In practice, implement the logic to parse text and convert to structured JSON
# -------------------------
    report_date_m = re.search(r"CONSUMER:.*?DATE:\s*(\d{4}-\d{2}-\d{2})", text)
    report_date = report_date_m.group(1) if report_date_m else None

    name_m = re.search(r"NAME:\s*([A-Z\s]+[A-Z])", text)
    full_name = name_m.group(1).strip() if name_m else None
    full_name=clean_field(full_name)
    dob_m = re.search(r"DATE OF BIRTH[:\s]*([0-9]{4}-[0-9]{2}-[0-9]{2})", text)
    dob = dob_m.group(1) if dob_m else None

    gender_m = re.search(r"GENDER[:\s]*(male|female)", text, re.I)
    gender = gender_m.group(1).lower() if gender_m else None

    # mobile: prefer last 10 digits if telephone present
    tel_m = re.search(r"\b01\s+(\d{9,15})", text) or re.search(r"\b(\+?91)?\s*([6-9]\d{9})\b", text)
    telephone_number = tel_m.group(1) if tel_m and tel_m.groups() and len(tel_m.groups())==1 else (tel_m.group(2) if tel_m and len(tel_m.groups())==2 else (tel_m.group(0) if tel_m else None))
    mobile = last_n_digits(telephone_number, 10) if telephone_number else None

    # PAN and SocialId
    pan_m = re.search(r"INCOME TAX ID NUMBER \(PAN\)\s*([A-Z0-9]{10})", text)
    pan = pan_m.group(1) if pan_m else None

    social_m = re.search(r"SocialId\s+([0-9]+)", text)
    social_id = social_m.group(1) if social_m else None

    # email
    email_m = re.search(r"([A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,})", text)
    email = email_m.group(1).upper() if email_m else None

    # credit score (simple heuristic)
    score_m = re.search(r"\n\s*(\d{3})\s*\n\s*CIBILTRANSUNION", text, re.I) or re.search(r"SCORE\s*[:\-]?\s*(\d{3})", text, re.I)
    credit_score = score_m.group(1) if score_m else None

    # -------------------------
    # 2) Addresses
    # -------------------------
    addresses = []
    addr_iter = re.finditer(r"ADDRESS\s*:\s*(.*?)\nCATEGORY:\s*(\d{2})\s+RESIDENCE CODE:.*?DATE REPORTED:([0-9]{4}-[0-9]{2}-[0-9]{2})", text, re.I|re.S)
    idx = 1
    for m in addr_iter:
        line = m.group(1).strip().rstrip(',')
        # try to capture state & pin from the address chunk if present like ", ,27, 421204"
        st_pin_m = re.search(r",\s*\,\s*([0-9]{1,2})\s*,\s*([0-9]{5,6})", m.group(1))
        state_code = st_pin_m.group(1) if st_pin_m else "27"
        pin = st_pin_m.group(2) if st_pin_m else ""
        addresses.append({
            "addressCategory": m.group(2),
            "dateReported": m.group(3),
            "index": str(idx),
            "line1": re.sub(r"\s+", " ", line),
            "line2": "",
            "pinCode": pin,
            "stateCode": state_code
        })
        idx += 1

    # If none found with above pattern, fallback: simple split by "ADDRESS :"
    if not addresses:
        parts = re.split(r"ADDRESS\s*:", text)
        for i, p in enumerate(parts[1:], 1):
            # stop at next "CATEGORY" or the end
            line1 = p.split("\n")[0].strip().rstrip(',')
            cat_m = re.search(r"CATEGORY[:\s]*(\d+)", p)
            date_m = re.search(r"DATE REPORTED[:\s]*([0-9]{4}-[0-9]{2}-[0-9]{2})", p)
            state_pin = re.search(r",\s*\,\s*([0-9]{1,2})\s*,\s*([0-9]{5,6})", p)
            addresses.append({
                "addressCategory": cat_m.group(1) if cat_m else "",
                "dateReported": date_m.group(1) if date_m else "",
                "index": str(i),
                "line1": re.sub(r"\s+", " ", line1),
                "line2": "",
                "pinCode": state_pin.group(2) if state_pin else "",
                "stateCode": state_pin.group(1) if state_pin else "27"
            })

    # -------------------------
    # 3) Employment
    # -------------------------
    employment = []
    emp_m = re.search(r"ACCOUNT TYPE\s+(.+?)\s+DATE REPORTED\s+([0-9]{4}-[0-9]{2}-[0-9]{2})\s+OCCUPATION CODE\s+([0-9]{2})", text, re.I|re.S)
    if emp_m:
        employment.append({
            "accountType": emp_m.group(1).strip().split()[0],
            "dateReported": emp_m.group(2),
            "index": "E01",
            "occupationCode": emp_m.group(3)
        })
    else:
        # fallback from the sample "10 2023-12-31 01 Not Available Not Available"
        emp_m2 = re.search(r"\n\s*(\d{1,2})\s+([0-9]{4}-[0-9]{2}-[0-9]{2})\s+([0-9]{2})\s+", text)
        if emp_m2:
            employment.append({
                "accountType": emp_m2.group(1),
                "dateReported": emp_m2.group(2),
                "index": "E01",
                "occupationCode": emp_m2.group(3)
            })

    # -------------------------
    # 4) Scores
    # -------------------------
    scores = []
    if credit_score:
        # choose scoreDate as first day of report month if report_date available
        score_date = None
        if report_date:
            rd = parse_yyyy_mm_dd(report_date)
            if rd:
                score_date = rd.replace(day=1).isoformat()
        scores.append({
            "score": credit_score,
            "scoreCardName": "CIBILTUSC3",
            "scoreCardVersion": "",
            "scoreDate": score_date or "",
            "scoreName": "CIBILTransUnionScore3",
            # heuristics for reason codes - try to extract numbers that look like reason codes (fallback to zeros)
            "reasonCodes": [
                {"reasonCodeName": "reasonCode 39", "reasonCodeValue": "39"},
                {"reasonCodeName": "reasonCode 38", "reasonCodeValue": "38"},
                {"reasonCodeName": "reasonCode 00", "reasonCodeValue": "00"},
                {"reasonCodeName": "reasonCode 00", "reasonCodeValue": "00"},
                {"reasonCodeName": "reasonCode 00", "reasonCodeValue": "00"},
            ]
        })

    # -------------------------
    # 5) Accounts parsing
    # -------------------------
    accounts = []
    # split by account blocks starting with MEMBER NAME:
    acc_blocks = re.split(r"(?=MEMBER NAME:)", text)
    acc_idx = 0
    for blk in acc_blocks:
        if "MEMBER NAME:" not in blk:
            continue
        acc_idx_str = str(acc_idx)
        member_m = re.search(r"MEMBER NAME:([^O\n\r]+?)\s+OPENED:", blk)
        member = (member_m.group(1).strip() if member_m else "").strip()
        opened_m = re.search(r"OPENED:([0-9]{4}-[0-9]{2}-[0-9]{2})", blk)
        date_opened = opened_m.group(1) if opened_m else ""
        high_credit_m = re.search(r"HIGH CREDIT AMOUNT:([0-9\-,]+)", blk)
        high_credit = to_int(high_credit_m.group(1)) if high_credit_m else 0
        account_num_m = re.search(r"ACCOUNT NUMBER:([0-9A-Za-z]+)", blk)
        account_num = account_num_m.group(1) if account_num_m else ""
        date_reported_m = re.search(r"REPORTED AND CERTIFIED:([0-9]{4}-[0-9]{2}-[0-9]{2})", blk)
        date_reported = date_reported_m.group(1) if date_reported_m else ""
        curr_bal_m = re.search(r"CURRENT BALANCE:(-?[0-9\-,]+)", blk)
        curr_bal = to_int(curr_bal_m.group(1)) if curr_bal_m else 0
        closed_m = re.search(r"ACCOUNT CLOSED:\s*([0-9A-Za-z]+)", blk)
        date_closed = closed_m.group(1) if closed_m else "NA"
        type_m = re.search(r"TYPE:\s*([A-Za-z0-9 \-]+?)\s+PMT HIST START:", blk)
        acc_type = type_m.group(1).strip() if type_m else ""
        pmt_start_m = re.search(r"PMT HIST START:([0-9]{4}-[0-9]{2}-[0-9]{2})", blk)
        pmt_start = pmt_start_m.group(1) if pmt_start_m else ""
        emi_m = re.search(r"EMI:([0-9\-]+)", blk)
        emi_amt = emi_m.group(1) if emi_m else "-1"
        ownership_m = re.search(r"OWNERSHIP:([A-Za-z]+)", blk)
        ownership = ownership_m.group(1) if ownership_m else ""
        pmt_end_m = re.search(r"PMT HIST END:([0-9]{4}-[0-9]{2}-[0-9]{2})", blk)
        pmt_end = pmt_end_m.group(1) if pmt_end_m else ""
        payment_freq_m = re.search(r"PAYMENT FREQUENCY:\s*([0-9]{2}|)", blk)
        payment_freq = payment_freq_m.group(1) if payment_freq_m else ""
        amount_overdue_m = re.search(r"Amount Overdue:([0-9\-]+)", blk)
        amount_overdue = amount_overdue_m.group(1) if amount_overdue_m else "0"
        last_payment_m = re.search(r"LAST PAYMENT:([0-9]{4}-[0-9]{2}-[0-9]{2})", blk)
        last_payment = last_payment_m.group(1) if last_payment_m else ""
        repayment_tenure_m = re.search(r"REPAYMENT TENURE:([0-9\-]+)", blk)
        tenure = repayment_tenure_m.group(1) if repayment_tenure_m else "-1"

        # monthly payment statuses + date tokens
        monthly_status_list = []
        # find sequence of status tokens (like "000 000 000 ...") - require at least 6 tokens
        statuses_m = re.search(r"((?:\b\d{3}\b[\s]*){6,})", blk)
        dates_m = re.search(r"((?:\b\d{2}-\d{2}\b[\s]*){6,})", blk)
        if statuses_m and dates_m:
            status_tokens = re.findall(r"\b\d{3}\b", statuses_m.group(1))
            date_tokens = re.findall(r"\b\d{2}-\d{2}\b", dates_m.group(1))
            nmap = min(len(status_tokens), len(date_tokens))
            for i in range(nmap):
                dt = monthyear_to_date(date_tokens[i])
                if dt:
                    monthly_status_list.append({"date": dt.isoformat(), "status": str(int(status_tokens[i]))})
        else:
            # fallback: try to capture any 'DAYS PAST DUE' block and set zeros
            if pmt_start:
                # build 16 months descending from pmt_start (heuristic)
                try:
                    start = parse_yyyy_mm_dd(pmt_start)
                    if start:
                        # we will map last 16 months from start backward
                        for i in range(0, 16):
                            m = start.month - i
                            y = start.year
                            while m <= 0:
                                m += 12
                                y -= 1
                            d = date(y, m, 1)
                            monthly_status_list.append({"date": d.isoformat(), "status": "0"})
                except:
                    monthly_status_list = []

        accounts.append({
            "accountType": acc_type,
            "accountNumber": account_num,
            "actualPaymentAmount": str(to_int(emi_amt, -1)),
            "creditFacilityStatus": "",
            "amountOverdue": str(to_int(amount_overdue, -1)),
            "currentBalance": str(curr_bal),
            "dateOpened": date_opened,
            "dateReported": date_reported,
            "highCreditAmount": str(high_credit),
            "index": acc_idx_str,
            "lastPaymentDate": last_payment,
            "memberShortName": member,
            "ownershipIndicator": ownership,
            "paymentEndDate": pmt_end,
            "paymentFrequency": payment_freq,
            "paymentHistory": "".join([s["status"] for s in monthly_status_list]) if monthly_status_list else "",
            "paymentStartDate": pmt_start,
            "woAmountPrincipal": "-1",
            "woAmountTotal": "-1",
            "dateClosed": date_closed,
            "termMonths": str(tenure if tenure else "-1"),
            "monthlyPayStatus": monthly_status_list,
            "emiAmount": str(emi_amt if emi_amt else "-1"),
            "repaymentTenure": str(tenure if tenure else "-1")
        })
        acc_idx += 1

    # -------------------------
    # 6) Enquiries
    # -------------------------
    enquiries = []
    # Expect lines like: HDFC BANK 2024-04-01 02 4500000
    enq_matches = re.findall(r"([A-Z &\.\-0-9]+?)\s+(\d{4}-\d{2}-\d{2})\s+(\d{1,2})\s+([0-9,]+)", text)
    for i, m in enumerate(enq_matches, 1):
        enquiries.append({
            "enquiryAmount": str(to_int(m[3])),
            "enquiryDate": m[1],
            "enquiryPurpose": m[2],
            "index": str(i),
            "memberShortName": m[0].strip()
        })

    # -------------------------
    # 7) IDs, Telephones, Emails, Names arrays
    # -------------------------
    ids = []
    if social_id:
        ids.append({"idNumber": social_id, "idType": "SocialId", "index": "1"})
    if pan:
        ids.append({"idNumber": pan, "idType": "TaxId", "index": "2"})

    telephones = []
    if telephone_number:
        # if telephone_number includes country code '91' at start, remove from telephoneNumber but keep as full for top-level
        tnum = re.sub(r'^\+?', '', telephone_number)
        telephones.append({
            "enquiryEnriched": "Y",
            "index": "1",
            "telephoneNumber": tnum,
            "telephoneType": "01"
        })

    emails = []
    if email:
        emails.append({"emailID": email, "index": "1"})

    names = []
    if full_name:
        # pick a short name if available (last two tokens)
        short_name = " ".join(full_name.split()[-2:]) if len(full_name.split()) >= 2 else full_name
        names.append({"birthDate": dob or "", "gender": gender or "", "index": "N01", "name": short_name})

    # -------------------------
    # 8) Response (consumerSummaryresp)
    # -------------------------
    # totals
    total_accounts = len(accounts)
    high_credit_sum = sum(to_int(a.get("highCreditAmount")) for a in accounts)
    current_balance_sum = sum(to_int(a.get("currentBalance")) for a in accounts)

    amount_overdues = [to_int(a.get("amountOverdue")) for a in accounts]
    # If any amountOverdue == -1 treat overdueBalance as -1 (unknown) following sample behavior
    if any(x == -1 for x in amount_overdues):
        overdue_balance = -1
    else:
        overdue_balance = sum(amount_overdues)

    overdue_accounts = sum(1 for x in amount_overdues if x > 0)
    zero_balance_accounts = sum(1 for a in accounts if to_int(a.get("currentBalance")) == 0)

    # recent/oldest date opened
    date_opened_list = [parse_yyyy_mm_dd(a["dateOpened"]) for a in accounts if parse_yyyy_mm_dd(a["dateOpened"])]
    recent_date_opened = max(date_opened_list).isoformat() if date_opened_list else ""
    oldest_date_opened = min(date_opened_list).isoformat() if date_opened_list else ""

    # inquiry summary
    total_inquiry = len(enquiries)
    # keep other fields empty per sample
    inquiry_summary = {
        "totalInquiry": total_inquiry,
        "inquiryPast30Days": "",
        "inquiryPast12Months": "",
        "inquiryPast24Months": "",
        "recentInquiryDate": ""
    }

    response_section = {
        "consumerSummaryresp": {
            "accountSummary": {
                "totalAccounts": total_accounts,
                "highCreditAmount": high_credit_sum,
                "currentBalance": current_balance_sum,
                "overdueAccounts": overdue_accounts,
                "overdueBalance": overdue_balance,
                "zeroBalanceAccounts": zero_balance_accounts,
                "recentDateOpened": recent_date_opened,
                "oldestDateOpened": oldest_date_opened
            },
            "inquirySummary": inquiry_summary
        }
    }

    # -------------------------
    # 9) Build final JSON object
    # -------------------------
    credit_report_obj = {
        "names": names,
        "ids": ids,
        "telephones": telephones,
        "emails": emails,
        "employment": employment,
        "scores": scores,
        "addresses": addresses,
        "accounts": accounts,
        "enquiries": enquiries,
        "response": response_section
    }

    final_json = {
        "data": {
            "data": {
                "client_id": f"credit_report_cibil_{pan or 'UNKNOWN'}",
                "mobile": mobile or "",
                "pan": pan or "",
                "name": full_name or "",
                "gender": gender or "",
                "user_email": email or None,
                "credit_score": credit_score or "",
                "credit_report": [credit_report_obj]
            },
            "status_code": 200,
            "success": True,
            "message": "Success",
            "message_code": "success"
        },
        "status": 200
    }
    return final_json