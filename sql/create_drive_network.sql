-- Table: public.route_api_drivenetwork

-- DROP TABLE public.route_api_drivenetwork;

CREATE TABLE public.route_api_drivenetwork
(
    id integer NOT NULL DEFAULT nextval('route_api_drivenetwork_id_seq'::regclass),
    start character varying(20) COLLATE pg_catalog."default" NOT NULL,
    "end" character varying(20) COLLATE pg_catalog."default" NOT NULL,
    geometry geometry(LineString,4326),
    CONSTRAINT route_api_drivenetwork_pkey PRIMARY KEY (id)
)
WITH (
    OIDS = FALSE
)
TABLESPACE pg_default;

ALTER TABLE public.route_api_drivenetwork
    OWNER to postgres;
-- Index: route_api_drivenetwork_geometry_id

-- DROP INDEX public.route_api_drivenetwork_geometry_id;

CREATE INDEX route_api_drivenetwork_geometry_id
    ON public.route_api_drivenetwork USING gist
    (geometry)
    TABLESPACE pg_default;