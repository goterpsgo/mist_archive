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
  ADD permission_id INT UNSIGNED,
  ADD CONSTRAINT FOREIGN KEY (permission_id) REFERENCES userPermissions(id)
;

# Assign "admin" as "Super User"
UPDATE mistUsers
SET permission_id = (
  select id from userPermissions
  where name = 'Super User'
)
WHERE username = 'admin';
