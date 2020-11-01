-- Table: public.route_api_crashes

-- DROP TABLE public.route_api_crashes;

CREATE TABLE public.route_api_crashes
(
    id integer NOT NULL DEFAULT nextval('route_api_crashes_id_seq'::regclass),
    hour integer NOT NULL,
    mode character varying(10) COLLATE pg_catalog."default" NOT NULL,
    geometry geometry(Point,4326),
    CONSTRAINT route_api_crashes_pkey PRIMARY KEY (id)
)
WITH (
    OIDS = FALSE
)
TABLESPACE pg_default;

ALTER TABLE public.route_api_crashes
    OWNER to postgres;
-- Index: route_api_crashes_geometry_id

-- DROP INDEX public.route_api_crashes_geometry_id;

CREATE INDEX route_api_crashes_geometry_id
    ON public.route_api_crashes USING gist
    (geometry)
    TABLESPACE pg_default;