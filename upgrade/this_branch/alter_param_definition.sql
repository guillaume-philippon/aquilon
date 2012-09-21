ALTER TABLE PARAM_DEFINITION ADD rebuild_required NUMBER(*,0);

UPDATE PARAM_DEFINITION SET rebuild_required = 0;

ALTER TABLE PARAM_DEFINITION add CONSTRAINT PARAM_DEFINITION_REBUILD_CK CHECK (rebuild_required IN (0, 1)) ENABLE;
ALTER TABLE PARAM_DEFINITION MODIFY (rebuild_required NUMBER(*,0) CONSTRAINT PARAM_DEFINITION_REBLD_REQ_NN NOT NULL);
COMMIT;
QUIT;
