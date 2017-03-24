ALTER TABLE parameter MODIFY (value CONSTRAINT parameter_value_nn NOT NULL);

ALTER TABLE parameter ADD holder_type VARCHAR2(16 CHAR);
ALTER TABLE parameter ADD personality_stage_id INTEGER;

UPDATE parameter SET holder_type = (SELECT holder_type FROM param_holder WHERE parameter.holder_id = param_holder.id);
ALTER TABLE parameter MODIFY (holder_type CONSTRAINT parameter_holder_type_nn NOT NULL);

UPDATE parameter SET personality_stage_id = (SELECT personality_stage_id FROM param_holder WHERE parameter.holder_id = param_holder.id);
ALTER TABLE parameter DROP COLUMN holder_id;

ALTER TABLE parameter ADD CONSTRAINT parameter_personality_stage_fk FOREIGN KEY (personality_stage_id) REFERENCES personality_stage (id) ON DELETE CASCADE;
ALTER TABLE parameter ADD CONSTRAINT parameter_personality_stage_uk UNIQUE (personality_stage_id);

DROP TABLE param_holder;
DROP SEQUENCE param_holder_id_seq;

ALTER TABLE param_def_holder ADD template VARCHAR2(32 CHAR);
ALTER TABLE param_def_holder DROP CONSTRAINT param_def_holder_archetype_uk;
DROP INDEX param_def_holder_archetype_uk;

INSERT INTO param_def_holder (id, "TYPE", creation_date, archetype_id, template)
	SELECT param_def_holder_id_seq.nextval, 'archetype', CURRENT_DATE,
		pdht.archetype_id, pdht.template
	FROM (
		SELECT DISTINCT pdh.archetype_id, pd.template
		FROM param_def_holder pdh JOIN param_definition pd ON pd.holder_id = pdh.id
		WHERE pdh."TYPE" = 'archetype'
	) pdht;

UPDATE param_definition SET holder_id = (
		SELECT pd2.id
		FROM param_def_holder pd1, param_def_holder pd2
		WHERE pd1.id = param_definition.holder_id AND
			pd1.archetype_id = pd2.archetype_id AND
			pd2.template = param_definition.template)
	WHERE template IS NOT NULL;
DELETE FROM param_def_holder WHERE "TYPE" = 'archetype' AND template IS NULL;

ALTER TABLE param_definition DROP COLUMN template;

ALTER TABLE param_def_holder ADD CONSTRAINT param_def_holder_arch_tmpl_uk UNIQUE (archetype_id, template);

QUIT;
