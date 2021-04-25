-- Exported from QuickDBD: https://www.quickdatabasediagrams.com/
-- Link to schema: https://app.quickdatabasediagrams.com/#/d/t1Otek


CREATE TABLE "users" (
    "id" int   NOT NULL,
    "first_name" string   NOT NULL,
    "last_name" string   NOT NULL,
    "username" string   NOT NULL,
    "password" string   NOT NULL,
    CONSTRAINT "pk_users" PRIMARY KEY (
        "id"
     )
);

CREATE TABLE "recipes" (
    "id" int   NOT NULL,
    "title" string   NOT NULL,
    "image" string   NOT NULL,
    "protien" int   NOT NULL,
    CONSTRAINT "pk_recipes" PRIMARY KEY (
        "id"
     )
);

CREATE TABLE "favorites" (
    "id" int   NOT NULL,
    "user_id" users   NOT NULL,
    "recipe_id" recipes   NOT NULL,
    "date_saved" date   NOT NULL,
    CONSTRAINT "pk_favorites" PRIMARY KEY (
        "id"
     )
);

CREATE TABLE "folder" (
    "id" int   NOT NULL,
    "name" string   NOT NULL,
    "user_id" int   NOT NULL,
    CONSTRAINT "pk_folder" PRIMARY KEY (
        "id"
     )
);

CREATE TABLE "saved_recipes" (
    "id" int   NOT NULL,
    "folder_id" int   NOT NULL,
    "recipe_id" int   NOT NULL,
    CONSTRAINT "pk_saved_recipes" PRIMARY KEY (
        "id"
     )
);

ALTER TABLE "favorites" ADD CONSTRAINT "fk_favorites_user_id" FOREIGN KEY("user_id")
REFERENCES "users" ("id");

ALTER TABLE "favorites" ADD CONSTRAINT "fk_favorites_recipe_id" FOREIGN KEY("recipe_id")
REFERENCES "recipes" ("id");

ALTER TABLE "folder" ADD CONSTRAINT "fk_folder_user_id" FOREIGN KEY("user_id")
REFERENCES "users" ("id");

ALTER TABLE "saved_recipes" ADD CONSTRAINT "fk_saved_recipes_folder_id" FOREIGN KEY("folder_id")
REFERENCES "folder" ("id");

ALTER TABLE "saved_recipes" ADD CONSTRAINT "fk_saved_recipes_recipe_id" FOREIGN KEY("recipe_id")
REFERENCES "recipes" ("id");

