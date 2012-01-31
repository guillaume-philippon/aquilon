-- Seems to work, network_type is not unique so no fkey for that.:w


-- alter service_map
ALTER TABLE SERVICE_MAP MODIFY(location_id null);
ALTER TABLE SERVICE_MAP ADD network_id INTEGER;

ALTER TABLE SERVICE_MAP ADD CONSTRAINT SVC_MAP_NET_FK FOREIGN KEY (network_id) REFERENCES network (id) ON DELETE CASCADE;

ALTER TABLE SERVICE_MAP DROP CONSTRAINT SVC_MAP_LOC_INST_UK;
DROP INDEX SVC_MAP_LOC_INST_UK;
ALTER TABLE SERVICE_MAP ADD CONSTRAINT SVC_MAP_LOC_NET_INST_UK UNIQUE (service_instance_id, location_id, network_id);

-- alter personality_service_map, same as for service_map
ALTER TABLE PERSONALITY_SERVICE_MAP MODIFY(location_id null);
ALTER TABLE PERSONALITY_SERVICE_MAP ADD network_id INTEGER;

ALTER TABLE PERSONALITY_SERVICE_MAP ADD CONSTRAINT PRSNLTY_SVC_MAP_NET_FK FOREIGN KEY (network_id) REFERENCES network (id) ON DELETE CASCADE;

ALTER TABLE PERSONALITY_SERVICE_MAP DROP CONSTRAINT PRSNLTY_SVC_MAP_LOC_INST_UK;
DROP INDEX PRSNLTY_SVC_MAP_LOC_INST_UK;
ALTER TABLE PERSONALITY_SERVICE_MAP ADD CONSTRAINT PRSNLTY_SVC_MAP_LOC_NET_INS_UK UNIQUE (personality_id, service_instance_id, location_id, network_id);

