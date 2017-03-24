CREATE SEQUENCE virtual_switch_seq;

CREATE TABLE virtual_switch (
	id INTEGER CONSTRAINT virtual_switch_id_nn NOT NULL,
	name VARCHAR2(63 CHAR) CONSTRAINT virtual_switch_name_nn NOT NULL,
	comments VARCHAR2(255 CHAR),
	creation_date DATE CONSTRAINT virtual_switch_cr_date_nn NOT NULL,
	CONSTRAINT virtual_switch_pk PRIMARY KEY (id),
	CONSTRAINT virtual_switch_name_uk UNIQUE (name)
);

CREATE TABLE vswitch_cluster (
	virtual_switch_id INTEGER CONSTRAINT vswitch_cluster_vswitch_id_nn NOT NULL,
	cluster_id INTEGER CONSTRAINT vswitch_cluster_cluster_id_nn NOT NULL,
	CONSTRAINT vswitch_cluster_pk PRIMARY KEY (virtual_switch_id, cluster_id),
	CONSTRAINT vswitch_cluster_vswitch_fk FOREIGN KEY (virtual_switch_id) REFERENCES virtual_switch (id),
	CONSTRAINT vswitch_cluster_cluster_fk FOREIGN KEY (cluster_id) REFERENCES clstr (id) ON DELETE CASCADE,
	CONSTRAINT vswitch_cluster_cluster_uk UNIQUE (cluster_id)
);

CREATE TABLE vswitch_host (
	virtual_switch_id INTEGER CONSTRAINT vswitch_host_vswitch_id_nn NOT NULL,
	host_id INTEGER CONSTRAINT vswitch_host_host_id_nn NOT NULL,
	CONSTRAINT vswitch_host_pk PRIMARY KEY (virtual_switch_id, host_id),
	CONSTRAINT vswitch_host_vswitch_fk FOREIGN KEY (virtual_switch_id) REFERENCES virtual_switch (id),
	CONSTRAINT vswitch_host_host_fk FOREIGN KEY (host_id) REFERENCES host (hardware_entity_id) ON DELETE CASCADE,
	CONSTRAINT vswitch_host_host_uk UNIQUE (host_id)
);

CREATE TABLE vswitch_pg (
	virtual_switch_id INTEGER CONSTRAINT vswitch_pg_vswitch_id_nn NOT NULL,
	port_group_id INTEGER CONSTRAINT vswitch_pg_port_group_id_nn NOT NULL,
	CONSTRAINT vswitch_pg_pk PRIMARY KEY (virtual_switch_id, port_group_id),
	CONSTRAINT vswitch_pg_vswitch_fk FOREIGN KEY (virtual_switch_id) REFERENCES virtual_switch (id) ON DELETE CASCADE,
	CONSTRAINT vswitch_pg_port_group_fk FOREIGN KEY (port_group_id) REFERENCES port_group (network_id) ON DELETE CASCADE
);

CREATE INDEX vswitch_pg_port_group_idx ON vswitch_pg (port_group_id);

QUIT;
