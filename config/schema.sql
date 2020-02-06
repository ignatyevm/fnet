CREATE TABLE "User" (
	"id" serial NOT NULL,
	"email" varchar(255) NOT NULL UNIQUE,
	"password_hash" TEXT NOT NULL,
	"first_name" varchar(50) NOT NULL,
	"last_name" varchar(50) NOT NULL,
	"gender" varchar(10) NOT NULL CONSTRAINT gender_constraint CHECK (gender in ('male', 'female')),
	"status" varchar(100),
	"birth_date" DATE NOT NULL,
	"register_date" DATE NOT NULL DEFAULT now(),
	"is_deleted" BOOLEAN NOT NULL DEFAULT false,
	"is_email_verified" BOOLEAN NOT NULL DEFAULT false,
	CONSTRAINT "User_pk" PRIMARY KEY ("id")
) WITH (
  OIDS=FALSE
);



CREATE TABLE "Post" (
	"id" serial NOT NULL,
	"profile_id" integer NOT NULL,
	"text" varchar(5000) NOT NULL,
	"likes_count" integer NOT NULL DEFAULT 0,
	"reposts_count" integer NOT NULL DEFAULT 0,
	"views_count" integer NOT NULL DEFAULT 0,
	"time" TIMESTAMP NOT NULL DEFAULT now(),
	CONSTRAINT "Post_pk" PRIMARY KEY ("id")
) WITH (
  OIDS=FALSE
);



CREATE TABLE "Dialog" (
	"id" serial NOT NULL,
	"second_member_id" integer NOT NULL,
	"first_member_id" integer NOT NULL,
	CONSTRAINT "Dialog_pk" PRIMARY KEY ("id")
) WITH (
  OIDS=FALSE
);



CREATE TABLE "Message" (
	"id" serial NOT NULL,
	"sender_id" integer NOT NULL,
	"dialog_id" serial NOT NULL,
	"text" varchar(1500) NOT NULL,
	"time" TIMESTAMP NOT NULL DEFAULT now(),
	"has_read" BOOLEAN NOT NULL DEFAULT false,
	CONSTRAINT "Message_pk" PRIMARY KEY ("id")
) WITH (
  OIDS=FALSE
);



CREATE TABLE "Session" (
	"id" serial NOT NULL,
	"user_id" integer NOT NULL UNIQUE,
	"token" TEXT NOT NULL UNIQUE,
	CONSTRAINT "Session_pk" PRIMARY KEY ("id")
) WITH (
  OIDS=FALSE
);



CREATE TABLE "FriendRequest" (
	"id" serial NOT NULL,
	"sender_id" integer NOT NULL UNIQUE,
	"receiver_id" integer NOT NULL UNIQUE,
	"time" TIMESTAMP NOT NULL DEFAULT now(),
	"is_accepted" BOOLEAN NOT NULL DEFAULT false,
	CONSTRAINT "FriendRequest_pk" PRIMARY KEY ("id")
) WITH (
  OIDS=FALSE
);



CREATE TABLE "Photo" (
	"id" serial NOT NULL,
	"owner_id" integer NOT NULL,
	"owner_type" varchar(10) NOT NULL,
	"path" TEXT NOT NULL UNIQUE,
	"time" TIMESTAMP NOT NULL DEFAULT now(),
	CONSTRAINT "Photo_pk" PRIMARY KEY ("id")
) WITH (
  OIDS=FALSE
);



CREATE TABLE "Comment" (
	"id" serial NOT NULL,
	"user_id" integer NOT NULL,
	"place_id" integer NOT NULL,
	"place_type" varchar(10) NOT NULL,
	"likes_count" integer NOT NULL,
	"text" TEXT(500) NOT NULL,
	"time" TIMESTAMP NOT NULL DEFAULT now(),
	CONSTRAINT "Comment_pk" PRIMARY KEY ("id")
) WITH (
  OIDS=FALSE
);



CREATE TABLE "Likes" (
	"user_id" integer NOT NULL,
	"place_type" varchar(10) NOT NULL,
	"place_id" integer NOT NULL
) WITH (
  OIDS=FALSE
);




ALTER TABLE "Post" ADD CONSTRAINT "Post_fk0" FOREIGN KEY ("profile_id") REFERENCES "User"("id");

ALTER TABLE "Dialog" ADD CONSTRAINT "Dialog_fk0" FOREIGN KEY ("second_member_id") REFERENCES "User"("id");
ALTER TABLE "Dialog" ADD CONSTRAINT "Dialog_fk1" FOREIGN KEY ("first_member_id") REFERENCES "User"("id");

ALTER TABLE "Message" ADD CONSTRAINT "Message_fk0" FOREIGN KEY ("sender_id") REFERENCES "User"("id");
ALTER TABLE "Message" ADD CONSTRAINT "Message_fk1" FOREIGN KEY ("dialog_id") REFERENCES "Dialog"("id");

ALTER TABLE "Session" ADD CONSTRAINT "Session_fk0" FOREIGN KEY ("user_id") REFERENCES "User"("id");

ALTER TABLE "FriendRequest" ADD CONSTRAINT "FriendRequest_fk0" FOREIGN KEY ("sender_id") REFERENCES "User"("id");
ALTER TABLE "FriendRequest" ADD CONSTRAINT "FriendRequest_fk1" FOREIGN KEY ("receiver_id") REFERENCES "User"("id");


ALTER TABLE "Comment" ADD CONSTRAINT "Comment_fk0" FOREIGN KEY ("user_id") REFERENCES "User"("id");

ALTER TABLE "Likes" ADD CONSTRAINT "Likes_fk0" FOREIGN KEY ("user_id") REFERENCES "User"("id");
