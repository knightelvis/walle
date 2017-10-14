
CREATE TABLE User(
    tlm_id VARCHAR(255),
    name VARCHAR(255)
);

CREATE TABLE Txn(
    from_user VARCHAR(255),
    to_user VARCHAR(255),
    amount INTEGER,
    reason VARCHAR(255),
    txn_date DATETIME # utc time
);

CREATE TABLE Balance (
    user VARCHAR(255),
    balance INTEGER
);
