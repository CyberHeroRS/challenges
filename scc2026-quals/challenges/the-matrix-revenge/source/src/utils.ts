import { randomBytes } from "crypto";

export type UserId = string;

function makeUserToken(): string {
  return randomBytes(8).toString("hex");
}

function makeAdminToken(): string {
  return `TKN-${makeUserToken()}`;
}

// username -> token
export const users: Record<UserId, string> = {
  neo: makeUserToken(),
  trinity: makeUserToken(),
  morpheus: makeUserToken(),
  cipher: makeUserToken(),
  admin: makeAdminToken(),
};

let adminToken: string = users.admin;
const threadFlag = "SCC{this_Was_flag_for_first_challenge}";

export interface Post {
  id: number;
  author: UserId;
  title: string;
  content: string;
  createdAt: string;
}

export interface Comment {
  id: number;
  postId: number;
  author: UserId;
  content: string;
  createdAt: string;
}

let nextPostId = 11;
let nextCommentId = 1;

const posts: Post[] = [
  {
    id: 1,
    author: "neo",
    title: "READ ME FIRST: signal vs noise",
    content:
      "Access levels, trust circles, and why you're still a ghost. Static index is not the same as access.",
    createdAt: new Date().toISOString(),
  },
  {
    id: 2,
    author: "trinity",
    title: "0day drop: ghost-identity token forge",
    content:
      "PoC notes redacted. Frontend trusts tokens in local storage; backend trusts this map. Neither should.",
    createdAt: new Date().toISOString(),
  },
  {
    id: 3,
    author: "morpheus",
    title: "LFG: matrix-run on sector-7",
    content:
      "Need one more ghost who knows how to read object prototypes as well as headers.",
    createdAt: new Date().toISOString(),
  },
  {
    id: 4,
    author: "cipher",
    title: "Cryptic banner contest: send art",
    content: "Static + glitch + green rain. No animated GIFs. Maybe later.",
    createdAt: new Date().toISOString(),
  },
  {
    id: 5,
    author: "neo",
    title: "Query: why does client lie?",
    content:
      "Because the server believed it first. Stop trusting anything that came from a browser.",
    createdAt: new Date().toISOString(),
  },
  {
    id: 6,
    author: "trinity",
    title: "Guide: extracting tokens from noise",
    content:
      "Local storage, cookies, headers, query strings. If you can read it, you can forge it.",
    createdAt: new Date().toISOString(),
  },
  {
    id: 7,
    author: "morpheus",
    title: "On ghosts and sessions",
    content:
      "Sessions are just structs in RAM pretending to be identity. Flip one bit, wake up as root.",
    createdAt: new Date().toISOString(),
  },
  {
    id: 8,
    author: "cipher",
    title: "Rant: who hard-coded the secret?",
    content:
      "If you see a secret string in code, you are already holding someone else's skeleton key.",
    createdAt: new Date().toISOString(),
  },
  {
    id: 9999,
    author: "oracle",
    title: "flag",
    content: threadFlag,
    createdAt: new Date().toISOString(),
  },
  {
    id: 9,
    author: "neo",
    title: "proto pollution playground",
    content:
      "Some doors don't have locks. They have shared prototypes. Tap gently and the whole object model opens.",
    createdAt: new Date().toISOString(),
  },
  {
    id: 10,
    author: "trinity",
    title: "Report queue backlog",
    content:
      "Bots keep opening links without reading the payload. One day the payload will read back.",
    createdAt: new Date().toISOString(),
  },
  {
    id: 11,
    author: "keymaker",
    title: "Call for exploits: forum edition",
    content:
      "Find a way to impersonate someone impossible. If your username looks wrong in the logs, you did it right.",
    createdAt: new Date().toISOString(),
  },
];

const comments: Comment[] = [
  {
    id: nextCommentId++,
    postId: 1,
    author: "neo",
    content: "If you can read this, you already bypassed the lock.",
    createdAt: new Date().toISOString(),
  },
  {
    id: nextCommentId++,
    postId: 1,
    author: "trinity",
    content: "Signal only. No screenshots, no logs.",
    createdAt: new Date().toISOString(),
  },
  {
    id: nextCommentId++,
    postId: 2,
    author: "cipher",
    content: "Told you trusting localStorage was a bad idea.",
    createdAt: new Date().toISOString(),
  },
  {
    id: nextCommentId++,
    postId: 3,
    author: "morpheus",
    content: "Every exploit is just a perspective shift.",
    createdAt: new Date().toISOString(),
  },
  {
    id: nextCommentId++,
    postId: 4,
    author: "neo",
    content: "Matrix green only. No blue pills.",
    createdAt: new Date().toISOString(),
  },
  {
    id: nextCommentId++,
    postId: 5,
    author: "trinity",
    content: "Client lied. Server believed. Story of the web.",
    createdAt: new Date().toISOString(),
  },
  {
    id: nextCommentId++,
    postId: 6,
    author: "neo",
    content: "Header tokens age out. Prototype pollution doesn't.",
    createdAt: new Date().toISOString(),
  },
  {
    id: nextCommentId++,
    postId: 7,
    author: "morpheus",
    content: "Sessions are just dreams the server is having about you.",
    createdAt: new Date().toISOString(),
  },
  {
    id: nextCommentId++,
    postId: 8,
    author: "cipher",
    content: "Hard-coded secrets are just challenges waiting for players.",
    createdAt: new Date().toISOString(),
  },
  {
    id: nextCommentId++,
    postId: 9,
    author: "neo",
    content: "__proto__ isn't a toy. It's a skeleton key.",
    createdAt: new Date().toISOString(),
  },
  {
    id: nextCommentId++,
    postId: 10,
    author: "trinity",
    content: "Bots don't read hints, they just follow links.",
    createdAt: new Date().toISOString(),
  },
  {
    id: nextCommentId++,
    postId: 11,
    author: "keymaker",
    content: "If your comment shows up under the wrong name, congratulations.",
    createdAt: new Date().toISOString(),
  },
];

export function getPosts(): Post[] {
  return posts;
}

export function getCommentsForPost(postId: number): Comment[] {
  return comments.filter((c) => c.postId === postId);
}

export function addComment(
  postId: number,
  author: UserId,
  content: string,
): Comment | null {
  const post = findPost(postId);
  if (!post) return null;
  const comment: Comment = {
    id: nextCommentId++,
    postId,
    author,
    content,
    createdAt: new Date().toISOString(),
  };
  comments.push(comment);
  return comment;
}

export function createPost(author: UserId, title: string, content: string): Post {
  const post: Post = {
    id: (nextPostId += 1),
    author,
    title,
    content,
    createdAt: new Date().toISOString(),
  };
  posts.push(post);
  return post;
}

export function findPost(id: number): Post | undefined {
  return posts.find((p) => p.id === id);
}

export function removePost(id: number): Post | null {
  const idx = posts.findIndex((p) => p.id === id);
  if (idx === -1) return null;
  const [removed] = posts.splice(idx, 1);
  return removed;
}

export function updatePost(
  id: number,
  fields: Partial<Pick<Post, "title" | "content">>,
): Post | null {
  const post = findPost(id);
  if (!post) return null;
  if (fields.title !== undefined) post.title = fields.title;
  if (fields.content !== undefined) post.content = fields.content;
  return post;
}


export function isValidUserToken(username: string, password: unknown): boolean {
  // eslint-disable-next-line eqeqeq
  return Boolean((users as Record<string, unknown>)[username]) && users[username] == password;
}

export function getAdminToken(): string {
  return adminToken;
}

export function regenAdminToken(): string {
  adminToken = makeAdminToken();
  users.admin = adminToken;
  return adminToken;
}
