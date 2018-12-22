SELECT investment_account, SUM(trading_vol) FROM trading_vol GROUP BY investment_account;

SELECT investment_account, trading_vol FROM trading_vol GROUP BY investment_account ORDER BY MAX(input_date);

SELECT investment_account FROM user WHERE referrer_account=='1030918';

SELECT MAX(input_date) FROM trading_vol;

SELECT investment_account, SUM(trading_vol) FROM trading_vol WHERE (investment_account IN (SELECT investment_account FROM user WHERE referrer_account=='1030918')) GROUP BY investment_account;

SELECT investment_account, trading_vol FROM trading_vol WHERE (investment_account IN (SELECT investment_account FROM user WHERE referrer_account=='1030918') AND input_date==(SELECT MAX(input_date) FROM trading_vol));


SELECT user.ib_name as '投资者', user.investment_account as '账户', SUM(trading_vol.trading_vol) AS '总交易量' FROM user LEFT JOIN trading_vol ON user.investment_account = trading_vol.investment_account WHERE user.referrer_account=='1030918' GROUP BY trading_vol.investment_account;


SELECT user.ib_name as '投资者', user.investment_account as '账户', trading_vol.trading_vol AS '上周交易量' FROM user LEFT JOIN trading_vol ON user.investment_account = trading_vol.investment_account WHERE (user.referrer_account=='1030918' AND trading_vol.input_date==(SELECT MAX(trading_vol.input_date) FROM trading_vol));

SELECT user.ib_name as '投资者', user.investment_account as '账户', trading_vol.trading_vol AS '上周交易量', commission_points.commission_points AS '点数', trading_vol.trading_vol*commission_points.commission_points AS '佣金' FROM user LEFT JOIN trading_vol ON user.investment_account = trading_vol.investment_account LEFT JOIN commission_points ON trading_vol.investment_account = commission_points.investment_account WHERE (user.referrer_account=='1030918' AND trading_vol.input_date==(SELECT MAX(trading_vol.input_date) FROM trading_vol));

SELECT commission.investment_account, user.ib_name, sum(commission.trading_vol), commission.commission_points, sum(commission.commission) FROM commission LEFT JOIN user ON user.investment_account = commission.investment_account WHERE commission.referrer_account=='1030918' GROUP BY commission.investment_account

SELECT commission.investment_account, user.ib_name, commission.trading_vol, commission.commission_points, commission.commission FROM commission LEFT JOIN user ON user.investment_account = commission.investment_account WHERE (commission.referrer_account=='1030918' AND commission.input_date==(SELECT MAX(commission.input_date) FROM commission))