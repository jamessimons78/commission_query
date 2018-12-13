CREATE TABLE IF NOT EXISTS [user](
  [id] INTEGER PRIMARY KEY AUTOINCREMENT, 
  [name] CHAR(20) NOT NULL, 
  [mobile_phone] CHAR(11), 
  [commission_account] CHAR(8), 
  [commission_password] CHAR(8), 
  [investment_account] CHAR(8), 
  [investment_password] CHAR(8), 
  [referrer_account] CHAR(8), 
  [referrer_name] CHAR(20), 
  [manager] BOOLEAN DEFAULT 0);
  
  CREATE TABLE IF NOT EXISTS [trading_vol](
  [investment_account] CHAR(8) NOT NULL, 
  [trading_vol] DECIMAL(6,2) NOT NULL, 
  [trading_week] INTEGER NOT NULL, 
  [statistics_date] TEXT(10) NOT NULL);