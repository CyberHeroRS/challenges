class NotesApp extends IntranetApp {
    constructor() {
        super();
        this.notesList = document.getElementById('notes-list');
        this.noteContent = document.getElementById('note-content');
        this.init();
    }

    async init() {
        try {
            const notes = await this.fetchNotes();
            this.renderNotesList(notes);
        } catch (error) {
            console.error('Failed to initialize notes:', error);
            if (error.message === 'Authentication failed') {
                window.location.href = '/login';
            }
        }
    }

    async fetchNotes() {
        const response = await this.authenticatedRequest('/api/notes');
        if (!response.ok) throw new Error('Failed to fetch notes');
        return await response.json();
    }

    async fetchNoteById(id) {
        const response = await this.authenticatedRequest(`/api/notes/${id}`);
        if (!response.ok) throw new Error('Failed to fetch note');
        return await response.json();
    }

    renderNotesList(notes) {
        this.notesList.innerHTML = notes.map(note => `
            <div class="note-item" data-id="${note._id.$oid}">
                <h3>${note.title}</h3>
                <p><b>Date:</b> ${new Date(note.created_at.$date).toLocaleString()}</p>
            </div>
        `).join('');

        this.notesList.addEventListener('click', async (e) => {
            const noteItem = e.target.closest('.note-item');
            if (noteItem) {
                const id = noteItem.dataset.id;
                const note = await this.fetchNoteById(id);
                this.renderNoteContent(note);
            }
        });
    }

    renderNoteContent(note) {
        this.noteContent.innerHTML = `
            <h2>${note.title}</h2>
            <div>${note.content.trim().replace("\n", "<br><br>")}</div>
        `;
    }
}

document.addEventListener('DOMContentLoaded', () => {
    new NotesApp();
});