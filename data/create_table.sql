CREATE TABLE IF NOT EXISTS [user](
  [ib_name] CHAR(20) NOT NULL, 
  [commission_account] CHAR(8) UNIQUE, 
  [password] CHAR(8), 
  [investment_account] CHAR(8) UNIQUE, 
  [referrer_account] CHAR(8), 
  [referrer_name] CHAR(20), 
  [manager] BOOLEAN DEFAULT 0, 
  [input_date] TEXT(10) NOT NULL, 
  [inputer] CHAR(8) NOT NULL);
  
  CREATE TABLE IF NOT EXISTS [trading_vol](
  [investment_account] CHAR(8) NOT NULL, 
  [trading_vol] DECIMAL(6, 2) NOT NULL, 
  [input_date] TEXT(10) NOT NULL, 
  [inputer] CHAR(8) NOT NULL);
  
  CREATE TABLE IF NOT EXISTS [dividend](
  [investment_account] CHAR(8) NOT NULL, 
  [dividend] DECIMAL(6, 2) NOT NULL, 
  [input_date] TEXT(10) NOT NULL, 
  [inputer] CHAR(8) NOT NULL);
  
  CREATE TABLE IF NOT EXISTS [commission_points](
  [investment_account] CHAR(8) NOT NULL, 
  [referrer_account] CHAR(8) NOT NULL, 
  [commission_points] INTEGER NOT NULL, 
  [input_date] TEXT(10) NOT NULL, 
  [inputer] CHAR(8) NOT NULL);
