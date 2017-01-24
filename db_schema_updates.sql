# update Assets.ip to handle IPv6 values
alter table Assets modify ip VARCHAR(39);

# Create new table userPermissions
create table userPermissions (
    id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY
  , name varchar(50)
);

# Populate table userPermissions
insert into userPermissions (name)
values
    ('No Permissions')
  , ('Normal User')
  , ('Admin User')
  , ('Super User')
;

# Update mistUsers
alter table mistUsers
  ADD permission_id INT UNSIGNED NOT NULL DEFAULT 1,
  ADD CONSTRAINT FOREIGN KEY (permission_id) REFERENCES userPermissions(id)
;

# Assign "admin" as "Super User"
UPDATE mistUsers
SET permission_id = (
  select id from userPermissions
  where name = 'Super User'
)
WHERE username = 'admin';

alter table mistUsers add unique (username);
alter table securityCenters add UNIQUE (fqdn_IP, serverName);

alter table userAccess add is_assigned timestamp;

# Add tag_definition_id to Tags table
# http://stackoverflow.com/a/15333484/6554056
alter table Tags add tag_definition_id INT;
update Tags t
  inner join tagDefinition td on t.rollup = td.rollup
set t.tag_definition_id = td.id;
alter table Tags add constraint foreign key (tag_definition_id) references tagDefinition(id);


# # NAME: sp_get_user
# # INPUT: mistUser id (INT) or username value (VARCHAR) or null
# # OUTPUT: 1st record that matches input else null set or all records
# NOTE: not used since sqlalchemy wasn't really designed to be used with stored procedures, but kept as reference - JWT Oct 2016
# DELIMITER $$
# DROP PROCEDURE IF EXISTS sp_get_user;
# CREATE PROCEDURE sp_get_user(
#     IN _user VARCHAR(200)
# )
#   BEGIN
#     SELECT mu.id as mistUser_id, mu.username, mu.permission, mu.subjectDN, mu.firstName, mu.lastName, mu.organization, mu.lockout, mu.permission_id
#       , up.name as permission_name
#     FROM mistUsers mu
#       LEFT JOIN userPermissions up on mu.permission = up.id
#     WHERE
#     IF (_user IS NOT NULL, IF (_user REGEXP '^[0-9]$', mu.id = CAST(_user AS UNSIGNED INT), mu.username = _user), 1=1)
#     ;
#   END $$
# DELIMITER ;
