create table authcasbin.user
(
    id              bigint(20) UNSIGNED auto_increment,
    username        varchar(150)                           not null comment '用户名(登录用户)',
    full_name       varchar(250)                           not null comment '全名',
    password        varchar(128)                           not null comment '密码',
    role_key        int          default -1 comment '关联角色id， 默认-1',
    email           varchar(150)                           not null comment '用户邮箱',
    is_superuser    tinyint(1)   default 0                 not null comment '是否超级用户',
    is_active       tinyint(1)   default 1                 not null comment '是否正常 (冻结)',
    last_login      datetime     default CURRENT_TIMESTAMP not null comment '最后登录时间',
    created_by      bigint       default -1                not null comment '创建人',
    avatar          varchar(250) default null comment '用户头像',
    remark          varchar(250) default '' comment '备注',
    create_time     bigint                                 not null comment '创建时间',
    update_time     bigint                                 not null comment '更新时间',
    md5_pw          char(32)     default ''                not null,
    last_reset_time datetime     default CURRENT_TIMESTAMP null,

    PRIMARY KEY (`id`) USING BTREE,
    UNIQUE KEY (`username`) USING BTREE,
    KEY `idx_create_time` (`create_time`) USING BTREE,
    KEY `idx_update_time` (`update_time`) USING BTREE

) ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4 COMMENT ='用户表';



create table authcasbin.role
(
    id          bigint(20) UNSIGNED auto_increment,
    role        varchar(32) unique  not null comment '角色名称',
    role_key    varchar(128) unique not null comment '角色标识',
    description varchar(128)        not null comment '角色描述',
    created_by  int                 not null comment '创建人',
    create_time bigint              not null comment '创建时间',
    update_time bigint              not null comment '更新时间',

    PRIMARY KEY (`id`) USING BTREE,
    UNIQUE KEY (`role`) USING BTREE,
    UNIQUE KEY (`role_key`) USING BTREE,
    key `created_by` (`created_by`) USING BTREE,
    KEY `idx_create_time` (`create_time`) USING BTREE,
    KEY `idx_update_time` (`update_time`) USING BTREE

) ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4 COMMENT ='角色表';

create table authcasbin.casbin_object
(
    id          bigint(20) UNSIGNED auto_increment,
    object_name varchar(128) unique not null comment '资源名称',
    object_key  varchar(128) unique not null comment '资源标识',
    description varchar(128) default null comment '资源描述',
    created_by  int                 not null comment '关联用户id',
    create_time bigint              not null comment '创建时间',
    update_time bigint              not null comment '更新时间',

    PRIMARY KEY (`id`) USING BTREE,
    UNIQUE KEY (`object_name`) USING BTREE,
    UNIQUE KEY (`object_key`) USING BTREE,
    key `created_by` (`created_by`) USING BTREE,
    KEY `idx_create_time` (`create_time`) USING BTREE,
    KEY `idx_update_time` (`update_time`) USING BTREE

) ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4 COMMENT ='casbin 资源表';


create table authcasbin.casbin_action
(
    id          bigint(20) UNSIGNED auto_increment,
    action_name varchar(128) unique not null comment '动作名称',
    action_key  varchar(128) unique not null comment '动作标识',
    description varchar(128) default null comment '动作描述',
    created_by  int                 not null comment '关联用户id',
    create_time bigint              not null comment '创建时间',
    update_time bigint              not null comment '更新时间',

    PRIMARY KEY (`id`) USING BTREE,
    UNIQUE KEY (`action_name`) USING BTREE,
    UNIQUE KEY (`action_key`) USING BTREE,
    key `created_by` (`created_by`) USING BTREE,
    KEY `idx_create_time` (`create_time`) USING BTREE,
    KEY `idx_update_time` (`update_time`) USING BTREE

) ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4 COMMENT ='casbin 资源行为表';


create table authcasbin.casbin_rule
(
    id    bigint(20) UNSIGNED auto_increment,
    ptype varchar(128) unique not null,
    v0    varchar(128),
    v1    varchar(128),
    v2    varchar(128),
    v3    varchar(128),
    v4    varchar(128),
    v5    varchar(128),

    PRIMARY KEY (`id`) USING BTREE

) ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4 COMMENT ='casbin 规则';