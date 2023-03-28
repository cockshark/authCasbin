create table r_cms_user_info
(
    id              bigint auto_increment
        primary key,
    username        varchar(150)                         not null comment '用户名(登录用户)',
    full_name       varchar(250)                         not null comment '全名',
    password        varchar(128)                         not null comment '密码',
    email           varchar(150)                         not null comment '用户邮箱',
    country_id      tinyint    default 0                 not null comment '用户国家',
    is_superuser    tinyint(1) default 0                 not null comment '超级用户',
    is_staff        tinyint(1) default 0                 not null comment '是否员工',
    is_active       tinyint(1) default 1                 not null comment '是否正常 (冻结)',
    last_login      datetime   default CURRENT_TIMESTAMP not null comment '最后登录时间',
    created_by      bigint     default -1                not null comment '创建人',
    create_time     bigint                               not null comment '创建时间',
    update_time     bigint                               not null comment '更新时间',
    md5_pw          char(32)   default ''                not null,
    last_reset_time datetime   default CURRENT_TIMESTAMP null,
    constraint username
        unique (username)
)
    comment '用户表';

create index create_time_idx
    on r_cms_user_info (create_time);



create table r_cms_user_group
(
    id          bigint auto_increment
        primary key,
    name        varchar(150)   not null comment '组(角色)名',
    created_by  int default -1 not null comment '创建人',
    create_time bigint         not null comment '创建时间',
    update_time bigint         not null comment '更新时间',
    constraint name
        unique (name)
)
    comment '用户组(角色表)';

create table r_cms_user_permission
(
    id          bigint auto_increment
        primary key,
    name        varchar(150)       not null comment '权限名字',
    backend_url text               not null comment '新增权限时配置的url',
    method      tinyint default 0  not null comment '目前没有用到, 为了后续支持http方法的权限校验',
    parent      bigint  default -1 not null comment '父权限',
    create_time bigint             not null comment '创建时间',
    update_time bigint             not null comment '更新时间'
)
    comment '权限表';


create table r_cms_user_userperm
(
    id          bigint auto_increment
        primary key,
    user_id     bigint not null comment '用户id',
    perm_id     bigint not null comment '权限id',
    create_time bigint not null comment '创建时间',
    update_time bigint not null comment '更新时间'
)
    comment '用户权限关联表';


create table r_cms_user_usergroup
(
    id          bigint auto_increment
        primary key,
    user_id     bigint not null comment '用户id',
    group_id    bigint not null comment '组id',
    create_time bigint not null comment '创建时间',
    update_time bigint not null comment '更新时间'
)
    comment '用户 用户组关联表';


create table r_cms_user_groupperm
(
    id          bigint auto_increment
        primary key,
    group_id    bigint not null comment '组id',
    perm_id     bigint not null comment '权限id',
    create_time bigint not null comment '创建时间',
    update_time bigint not null comment '更新时间'
)
    comment '用户组权限关联表';