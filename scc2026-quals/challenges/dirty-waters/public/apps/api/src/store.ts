import { customAlphabet } from "nanoid";
import type { PostRecord, ReportRecord, SessionRecord, UserRecord } from "./types.js";

const nanoid = customAlphabet("1234567890abcdefghijklmnopqrstuvwxyz", 12);
const adminPassword = process.env.ADMIN_PASSWORD ?? "adminpanel!2026";
const flag = process.env.FLAG ?? "SCC{threadboard_flag_placeholder}";

const users = new Map<string, UserRecord>([
  [
    "admin",
    {
      id: nanoid(),
      username: "admin",
      password: adminPassword,
      role: "admin",
      permissions: {
        moderator: true
      },
      badges: ["staff", "founder"],
      displayName: "chief_mod",
      bio: "Head moderator account.",
      preferences: {
        theme: {
          cardStyle: "clean",
          accentColor: "orange"
        },
        dashboard: {
          compact: false
        }
      }
    }
  ],
  [
    "guest",
    {
      id: nanoid(),
      username: "guest",
      password: "guestpass123",
      role: "user",
      displayName: "nova_guest",
      bio: "Testing layouts, writing tiny notes, and reporting suspicious posts.",
      preferences: {
        theme: {
          cardStyle: "soft",
          accentColor: "blue"
        },
        dashboard: {
          compact: false
        }
      }
    }
  ]
]);

const usersById = new Map(Array.from(users.values()).map((user) => [user.id, user]));
const sessions = new Map<string, SessionRecord>();

const posts: PostRecord[] = [
  {
    id: nanoid(),
    author: "admin",
    title: "Welcome to ThreadBoard",
    body: "Small communities, simple posts, and quick moderation reports all in one place. Staff can export audit logs from /api/mod/logs/export.",
    createdAt: "2026-03-13T10:00:00Z"
  },
  {
    id: nanoid(),
    author: "guest",
    title: "Trying the new profile settings",
    body: "The live preview is nice. I hope nobody makes it weird.",
    createdAt: "2026-03-14T18:10:00Z"
  }
];

const reports: ReportRecord[] = [];

export function authenticate(username: string, password: string) {
  const user = users.get(username);
  if (!user || user.password !== password) {
    return null;
  }

  return user;
}

export function createUser(username: string, password: string) {
  if (users.has(username)) {
    return { error: "Username already exists." as const };
  }

  const user: UserRecord = {
    id: nanoid(),
    username,
    password,
    role: "user",
    displayName: username,
    bio: "New ThreadBoard member.",
    preferences: {
      theme: {
        cardStyle: "clean",
        accentColor: "green"
      },
      dashboard: {
        compact: false
      }
    }
  };

  users.set(username, user);
  usersById.set(user.id, user);
  return { user };
}

export function createSession(userId: string) {
  const sessionId = nanoid();
  sessions.set(sessionId, { userId, createdAt: Date.now() });
  return sessionId;
}

export function destroySession(sessionId?: string) {
  if (sessionId) {
    sessions.delete(sessionId);
  }
}

export function getUserBySession(sessionId?: string) {
  if (!sessionId) {
    return null;
  }

  const session = sessions.get(sessionId);
  if (!session) {
    return null;
  }

  return usersById.get(session.userId) ?? null;
}

export function getSafeViewer(user: UserRecord) {
  return {
    username: user.username,
    role: user.role,
    displayName: user.displayName,
    bio: user.bio,
    preferences: user.preferences
  };
}

export function listPosts() {
  return posts.slice().reverse();
}

export function createPost(author: string, title: string, body: string) {
  const post: PostRecord = {
    id: nanoid(),
    author,
    title,
    body,
    createdAt: new Date().toISOString()
  };

  posts.unshift(post);
  return post;
}

export function updateProfile(username: string, displayName: string, bio: string) {
  const user = users.get(username);
  if (!user) {
    return null;
  }

  user.displayName = displayName;
  user.bio = bio;
  return user;
}

function applyThemePatch(target: Record<string, unknown>, source: Record<string, unknown>) {
  for (const key of Object.keys(source)) {
    const value = source[key];
    if (Array.isArray(value)) {
      target[key] = [...value];
      continue;
    }

    if (typeof value === "object" && value !== null) {
      if (!target[key]) {
        target[key] = {};
      }

      applyThemePatch(
        target[key] as Record<string, unknown>,
        value as Record<string, unknown>
      );
      continue;
    }

    target[key] = value;
  }
}

function normalizeImportPayload(payload: Record<string, unknown>) {
  for (const key in payload) {
    const value = payload[key];
    if (key === "__proto__") {
      delete payload[key];
      continue;
    }

    if (typeof value === "object" && value !== null && !Array.isArray(value)) {
      normalizeImportPayload(value as Record<string, unknown>);
    }
  }
}

export function applyImportedPreferences(username: string, payload: Record<string, unknown>) {
  const user = users.get(username);
  if (!user) {
    return null;
  }

  normalizeImportPayload(payload);
  applyThemePatch(user.preferences as unknown as Record<string, unknown>, payload);
  return user;
}

export function createReport(reporter: string, url: string, reason: string) {
  const report: ReportRecord = {
    id: nanoid(),
    reporter,
    url,
    reason,
    createdAt: new Date().toISOString()
  };

  reports.unshift(report);
  return report;
}

export function listReports() {
  return reports;
}

function rot13(input: string) {
  return input.replace(/[a-zA-Z]/g, (char) => {
    const base = char <= "Z" ? 65 : 97;
    return String.fromCharCode(((char.charCodeAt(0) - base + 13) % 26) + base);
  });
}

function encodeArchivePart(value: string) {
  return Buffer.from(rot13(value.split("").reverse().join(""))).toString("base64");
}

export function readModeratorArchive(user: UserRecord) {
  const hasModeratorPermission = user.permissions?.moderator === true;
  const hasStaffBadge = Array.isArray(user.badges) && user.badges.includes("staff");
  if (!hasModeratorPermission || !hasStaffBadge) {
    return null;
  }

  const pivot = Math.max(1, Math.floor(flag.length / 3));
  const partA = encodeArchivePart(flag.slice(0, pivot));
  const partB = encodeArchivePart(flag.slice(pivot, pivot * 2));
  const partC = encodeArchivePart(flag.slice(pivot * 2));

  return {
    records: [
      { category: "ops", status: "ok" },
      { category: "appeals", status: "ok" },
      { category: "abuse", status: "ok" }
    ],
    codec: "base64(rot13(reverse(part)))",
    payload: [partA, partB, partC]
  };
}
