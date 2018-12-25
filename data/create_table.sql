CREATE TABLE IF NOT EXISTS [user](
  [ib_name] CHAR(20) NOT NULL, 
  [commission_account] CHAR(7) UNIQUE, 
  [password] CHAR(8), 
  [investment_account] CHAR(7) UNIQUE, 
  [referrer_account] CHAR(7), 
  [referrer_name] CHAR(20), 
  [manager] BOOLEAN DEFAULT 0, 
  [input_date] TEXT(10) NOT NULL, 
  [inputer] CHAR(7) NOT NULL);
  
CREATE TABLE IF NOT EXISTS [trading_vol](
  [investment_account] CHAR(7) NOT NULL, 
  [trading_vol] DECIMAL(6, 2) NOT NULL, 
  [input_date] TEXT(10) NOT NULL, 
  [inputer] CHAR(7) NOT NULL);
  
CREATE TABLE IF NOT EXISTS [dividend](
  [investment_account] CHAR(7) NOT NULL, 
  [dividend] DECIMAL(6, 2) NOT NULL, 
  [input_date] TEXT(10) NOT NULL, 
  [inputer] CHAR(7) NOT NULL);
  
CREATE TABLE IF NOT EXISTS [commission_points](
  [investment_account] CHAR(7) NOT NULL, 
  [referrer_account] CHAR(7) NOT NULL, 
  [commission_points] DECIMAL(5, 2) NOT NULL, 
  [input_date] TEXT(10) NOT NULL, 
  [inputer] CHAR(7) NOT NULL);

CREATE TABLE IF NOT [commission](
  [investment_account] CHAR(7) NOT NULL, 
  [trading_vol] DECIMAL(6, 2) NOT NULL, 
  [referrer_account] CHAR(7) NOT NULL, 
  [commission_points] INTEGER NOT NULL, 
  [commission] DECIMAL(8, 2) NOT NULL, 
  [input_date] TEXT(10) NOT NULL, 
  [inputer] CHAR(7) NOT NULL);
  
CREATE TABLE IF NOT [leader](
  [commission_account] CHAR(7) NOT NULL UNIQUE, 
  [ib_name] CHAR(20) NOT NULL, 
  [max_commission_points] DECIMAL(5, 2) NOT NULL DEFAULT 8, 
  [max_dividend_points] DECIMAL(4, 2) NOT NULL DEFAULT (0.5), 
  [referrer_account] CHAR(7) NOT NULL, 
  [browse_commission_yn] BOOLEAN DEFAULT 1, 
  [add_ib_yn] BOOLEAN DEFAULT 1, 
  [entering_vol_yn] BOOLEAN DEFAULT 0, 
  [input_date] TEXT(10) NOT NULL, 
  [inputer] CHAR(7) NOT NULL);