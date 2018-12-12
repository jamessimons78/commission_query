CREATE TABLE IF NOT EXISTS [users](
  [id] INTEGER PRIMARY KEY AUTOINCREMENT, 
  [name] CHAR(20) NOT NULL, 
  [mobile_phone] CHAR(11), 
  [commission_account] CHAR(8), 
  [commission_password] CHAR(8), 
  [investment_account] CHAR(8), 
  [investment_password] CHAR(8), 
  [referrer_name] CHAR(20), 
  [referrals_account] TEXT, 
  [referrals_name] TEXT, 
  [manager] BOOLEAN DEFAULT 0);