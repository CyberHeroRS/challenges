export {};

declare global {
  interface Window {
    ThreadBoardPreview: {
      renderDisplayNamePreview: (targetId: string, displayName: string) => void;
    };
  }
}
