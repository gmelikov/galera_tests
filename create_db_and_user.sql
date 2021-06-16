create database lock_tests;

CREATE USER 'lock_user_test'@'%' IDENTIFIED BY 'lock_password';

GRANT ALL ON lock_tests.* TO 'lock_user_test'@'%';

FLUSH privileges;

use lock_tests;

CREATE TABLE `endpoints` (
  `uuid` char(36) NOT NULL,
  `switch` char(36) DEFAULT NULL,
  `port` smallint(5) unsigned DEFAULT NULL,
  `vlan` smallint(5) unsigned DEFAULT NULL,
  PRIMARY KEY (`uuid`),
  UNIQUE KEY `switch_port_vlan_idx` (`switch`,`port`,`vlan`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE `links` (
  `uuid` char(36) NOT NULL,
  `src_endpoint` char(36) NOT NULL,
  `dst_endpoint` char(36) NOT NULL,
  `endpoints_hash` char(32) NOT NULL,
  PRIMARY KEY (`uuid`),
  KEY `src_endpoin_idx` (`src_endpoint`),
  KEY `dst_endpoin_idx` (`dst_endpoint`),
  CONSTRAINT `fk_links_dst_endpoint` FOREIGN KEY (`dst_endpoint`) REFERENCES `endpoints` (`uuid`),
  CONSTRAINT `fk_links_src_endpoint` FOREIGN KEY (`src_endpoint`) REFERENCES `endpoints` (`uuid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

insert into endpoints (uuid, port) values ('00046958-42eb-4c4b-bab9-f2bc16673d01', 1),
                                    ('00046958-42eb-4c4b-bab9-f2bc16673d02', 2),
                                    ('00046958-42eb-4c4b-bab9-f2bc16673d03', 3),
                                    ('00046958-42eb-4c4b-bab9-f2bc16673d04', 4),
                                    ('00046958-42eb-4c4b-bab9-f2bc16673d05', 5),
                                    ('00046958-42eb-4c4b-bab9-f2bc16673d06', 6);

insert into links (uuid, src_endpoint, dst_endpoint, endpoints_hash) values
    ('00047d69-1799-4a4c-ab20-9a74a45d8a01', '00046958-42eb-4c4b-bab9-f2bc16673d01','00046958-42eb-4c4b-bab9-f2bc16673d02','1'),
    ('00047d69-1799-4a4c-ab20-9a74a45d8a02', '00046958-42eb-4c4b-bab9-f2bc16673d03','00046958-42eb-4c4b-bab9-f2bc16673d04','2');
