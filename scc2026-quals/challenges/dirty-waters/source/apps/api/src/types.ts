export type Role = "admin" | "user";

export type UserRecord = {
  id: string;
  username: string;
  password: string;
  role: Role;
  permissions?: {
    moderator?: boolean;
  };
  badges?: string[];
  displayName: string;
  bio: string;
  preferences: {
    theme: {
      cardStyle: string;
      accentColor: string;
    };
    dashboard: {
      compact: boolean;
    };
  };
};

export type SessionRecord = {
  userId: string;
  createdAt: number;
};

export type PostRecord = {
  id: string;
  author: string;
  title: string;
  body: string;
  createdAt: string;
};

export type ReportRecord = {
  id: string;
  reporter: string;
  url: string;
  reason: string;
  createdAt: string;
};
