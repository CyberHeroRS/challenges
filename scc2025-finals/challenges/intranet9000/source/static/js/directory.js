class DirectoryApp extends IntranetApp {
    constructor() {
        super();
        this.searchForm = document.getElementById('searchForm');
        this.loadingIndicator = document.getElementById('loadingIndicator');
        this.resultsContainer = document.getElementById('resultsContainer');
        this.init();
    }

    init() {
        this.searchForm.addEventListener('submit', (e) => {
            e.preventDefault();
            this.loadResults();
        });

        // Load initial results
        this.loadResults();
    }

    async loadResults() {
        this.loadingIndicator.style.display = 'block';
        this.resultsContainer.innerHTML = '';

        const formData = new FormData(this.searchForm);
        // Check if the search query is empty
        if (formData.get('first_name') === '' && formData.get('last_name') === '' && formData.get('department') === '') {
            this.loadingIndicator.style.display = 'none';
            this.resultsContainer.innerHTML = '<p>Use the fields above to search or filter</p>';
            return;
        }

        const queryString = new URLSearchParams(formData).toString();

        try {
            const response = await this.unauthenticatedRequest(`/api/directory?${queryString}`);
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            const data = await response.json();

            this.loadingIndicator.style.display = 'none';

            if (data.items && data.items.length > 0) {
                const tableRows = data.items.map(item => `
                    <tr>
                        <td>${item.first_name}</td>
                        <td>${item.last_name}</td>
                        <td>${item.department}</td>
                        ${item.is_public 
                            ? `<td>${item.phone_number}</td><td>${item.email}</td>`
                            : '<td colspan="2" class="redacted">only visible to employees</td>'
                        }
                    </tr>
                `).join('');

                const table = `
                    <table>
                        <tr>
                            <th>First Name</th>
                            <th>Last Name</th>
                            <th>Department</th>
                            <th>Phone Number</th>
                            <th>Email</th>
                        </tr>
                        ${tableRows}
                    </table>
                `;

                this.resultsContainer.innerHTML = table;
            } else {
                this.resultsContainer.innerHTML = '<p>No results found</p>';
            }
        } catch (error) {
            console.error('Error:', error);
            this.loadingIndicator.style.display = 'none';
            this.resultsContainer.innerHTML = '<p>An error occurred while fetching results</p>';
            if (error.message === 'Authentication failed') {
                window.location.href = '/login';
            }
        }
    }
}