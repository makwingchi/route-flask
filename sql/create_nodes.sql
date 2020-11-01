-- Table: public.route_api_drivenodes

-- DROP TABLE public.route_api_drivenodes;

CREATE TABLE public.route_api_drivenodes
(
    id integer NOT NULL DEFAULT nextval('route_api_drivenodes_id_seq'::regclass),
    osmid character varying(20) COLLATE pg_catalog."default" NOT NULL,
    geometry geometry(Point,4326),
    CONSTRAINT route_api_drivenodes_pkey PRIMARY KEY (id)
)
WITH (
    OIDS = FALSE
)
TABLESPACE pg_default;

ALTER TABLE public.route_api_drivenodes
    OWNER to postgres;
-- Index: route_api_drivenodes_geometry_id

-- DROP INDEX public.route_api_drivenodes_geometry_id;

CREATE INDEX route_api_drivenodes_geometry_id
    ON public.route_api_drivenodes USING gist
    (geometry)
    TABLESPACE pg_default;