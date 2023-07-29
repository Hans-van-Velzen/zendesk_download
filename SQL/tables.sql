
create table zendesk.groups (
    id  bigint,
    jdoc jsonb
);
-- create table zendesk.groups (
--     id  bigint,
--     is_public boolean,
--     url varchar(255),
--     name varchar(255),
--     description text,
--     "default" boolean,
--     deleted boolean,
--     created_at varchar(20),
--     updated_at varchar(20)
-- );

create table zendesk.users (
    id  bigint,
    jdoc jsonb
);

-- CREATE TABLE zendesk.users (
-- 	id bigint NOT NULL,
-- 	url text NULL,
-- 	"name" text NULL,
-- 	email text NULL,
-- 	created_at text NULL,
-- 	updated_at text NULL,
-- 	time_zone text NULL,
-- 	iana_time_zone text NULL,
-- 	phone text NULL,
-- 	shared_phone_number text NULL,
-- 	photo text NULL,
-- 	locale_id int8 NULL,
-- 	locale text NULL,
-- 	organization_id int8 NULL,
-- 	"role" text NULL,
-- 	verified bool NULL,
-- 	external_id text NULL,
-- 	tags text NULL,
-- 	alias text NULL,
-- 	active bool NULL,
-- 	shared bool NULL,
-- 	shared_agent bool NULL,
-- 	last_login_at text NULL,
-- 	two_factor_auth_enabled text NULL,
-- 	signature text NULL,
-- 	details text NULL,
-- 	notes text NULL,
-- 	role_type int8 NULL,
-- 	custom_role_id int8 NULL,
-- 	moderator bool NULL,
-- 	ticket_restriction text NULL,
-- 	only_private_comments bool NULL,
-- 	restricted_agent bool NULL,
-- 	suspended bool NULL,
-- 	default_group_id int8 NULL,
-- 	report_csv bool NULL,
-- 	user_fields jsonb NULL,
-- 	CONSTRAINT users_pkey PRIMARY KEY (id)
-- );

create table zendesk.tickets (
    id  bigint,
    jdoc jsonb
);

create table zendesk.comments (
    id  bigint,
    jdoc jsonb
);
