CREATE DATABASE $(SQL_DATABASE)
GO

ALTER DATABASE $(SQL_DATABASE) SET RECOVERY BULK_LOGGED
GO


USE $(SQL_DATABASE)
GO

CREATE TABLE budget
(
    id         INT IDENTITY PRIMARY KEY,
    created_at DATETIME     NOT NULL,
    name       VARCHAR(255) NOT NULL UNIQUE
)
GO

CREATE TABLE category
(
    id          INT IDENTITY PRIMARY KEY,
    created_at  DATETIME     NOT NULL,
    name        VARCHAR(255) NOT NULL UNIQUE,
    description VARCHAR(1023)
)
GO

CREATE TABLE [transaction]
(
    id          INT IDENTITY PRIMARY KEY,
    created_at  DATETIME NOT NULL,
    amount      float    NOT NULL,
    description VARCHAR(1023),
    category_id INT CONSTRAINT transaction_category_fk REFERENCES category,
    budget_id   INT CONSTRAINT transaction_budget_fk REFERENCES $(SQL_DATABASE)
)
GO

CREATE TABLE [user]
(
    id         INT IDENTITY PRIMARY KEY,
    created_at DATETIME NOT NULL,
    email      VARCHAR(255) NOT NULL UNIQUE,
    password   VARCHAR(100) NOT NULL UNIQUE
)
GO

CREATE TABLE user_to_budget
(
    id         INT IDENTITY PRIMARY KEY,
    created_at DATETIME NOT NULL,
    budget_id  INT CONSTRAINT user_to_budget_budget_fk REFERENCES $(SQL_DATABASE),
    user_id    INT CONSTRAINT user_to_budget_user_fk REFERENCES [user]
)
GO
