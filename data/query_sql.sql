SELECT investment_account, SUM(trading_vol) FROM trading_vol GROUP BY investment_account;

SELECT investment_account, trading_vol FROM trading_vol GROUP BY investment_account ORDER BY MAX(input_date);

SELECT investment_account FROM user WHERE referrer_account=='1030918';

SELECT MAX(input_date) FROM trading_vol;

SELECT investment_account, SUM(trading_vol) FROM trading_vol WHERE (investment_account IN (SELECT investment_account FROM user WHERE referrer_account=='1030918')) GROUP BY investment_account;

SELECT investment_account, trading_vol FROM trading_vol WHERE (investment_account IN (SELECT investment_account FROM user WHERE referrer_account=='1030918') AND input_date==(SELECT MAX(input_date) FROM trading_vol)) GROUP BY investment_account;