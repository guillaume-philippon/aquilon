CREATE SEQUENCE personality_stage_id_seq;

CREATE TABLE personality_stage (
	id INTEGER CONSTRAINT personality_stage_id_nn NOT NULL,
	personality_id INTEGER CONSTRAINT personality_stage_pers_id_nn NOT NULL,
	name VARCHAR2(8 CHAR) CONSTRAINT personality_stage_name_nn NOT NULL,
	CONSTRAINT personality_stage_pers_fk FOREIGN KEY (personality_id) REFERENCES personality (id) ON DELETE CASCADE,
	CONSTRAINT personality_stage_pk PRIMARY KEY (id),
	CONSTRAINT personality_stage_uk UNIQUE (personality_id, name)
);

ALTER TABLE host ADD personality_stage_id INTEGER;
ALTER TABLE clstr ADD personality_stage_id INTEGER;

DECLARE
	CURSOR pers_curs IS SELECT id FROM personality;
	pers_rec pers_curs%ROWTYPE;
	vers_id NUMBER;
BEGIN
	FOR pers_rec IN pers_curs LOOP
		INSERT INTO personality_stage (id, personality_id, name)
			VALUES (personality_stage_id_seq.NEXTVAL, pers_rec.id, 'current')
			RETURNING id INTO vers_id;
		UPDATE host SET personality_stage_id = vers_id WHERE personality_id = pers_rec.id;
		UPDATE clstr SET personality_stage_id = vers_id WHERE personality_id = pers_rec.id;
	END LOOP;
END;
/

COMMIT;

ALTER TABLE host MODIFY (personality_stage_id INTEGER CONSTRAINT host_personality_stage_id_nn NOT NULL);
ALTER TABLE host ADD CONSTRAINT host_personality_stage_fk
	FOREIGN KEY (personality_stage_id) REFERENCES personality_stage (id);
ALTER TABLE host DROP COLUMN personality_id;
CREATE INDEX host_personality_stage_idx ON host (personality_stage_id);

ALTER TABLE clstr MODIFY (personality_stage_id INTEGER CONSTRAINT clstr_personality_stage_id_nn NOT NULL);
ALTER TABLE clstr ADD CONSTRAINT clstr_personality_stage_fk
	FOREIGN KEY (personality_stage_id) REFERENCES personality_stage (id);
ALTER TABLE clstr DROP COLUMN personality_id;
CREATE INDEX clstr_personality_stage_idx ON clstr (personality_stage_id);

QUIT;
