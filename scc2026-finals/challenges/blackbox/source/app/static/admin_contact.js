// Admin Contact Search - JavaScript functionality
document.addEventListener('DOMContentLoaded', function() {
    const searchForm = document.querySelector('form');
    const submitButton = searchForm.querySelector('button[type="submit"]');
    
    if (searchForm && submitButton) {
        submitButton.addEventListener('click', function(e) {
            e.preventDefault();
            
            const emailInput = searchForm.querySelector('input[name="email"]');
            const email = emailInput.value.trim();
            
            if (!email) {
                displayError('Please enter an email address');
                return;
            }
            
            
            // Build XML payload
            const xmlPayload = `<?xml version="1.0"?>
<search>
    <email>${email}</email>
</search>`;
                        
            // Send POST request with XML
            fetch('/admin/contacts', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/xml'
                },
                body: xmlPayload
            })
            .then(response => {
                return response.text();
            })
            .then(xmlText => {
                displayResults(xmlText);
            })
            .catch(error => {
                displayError('An error occurred while searching contacts: ' + error.message);
            });
        });
    }
});


function displayResults(responseText) {
    
    const container = document.querySelector('.col-lg-10');
    
    let resultsDiv = document.querySelector('.results-table');
    if (!resultsDiv) {
        resultsDiv = document.createElement('div');
        resultsDiv.className = 'results-table';
        if (container) {
            container.appendChild(resultsDiv);
        }
    }
    
    const lines = responseText.split('\n');
    const contacts = [];
    let inResultsSection = false;
    let searchedFor = '';
    
    for (let line of lines) {
        if (line.includes('You searched for:')) {
            searchedFor = line;
        } else if (line.includes('Results:')) {
            inResultsSection = true;
        } else if (inResultsSection && line.trim()) {
            // Parse contact line: "UUID: ..., Email: ..."
            const match = line.match(/UUID:\s*([^,]+),\s*Email:\s*(.+)/);
            if (match) {
                contacts.push({
                    uuid: match[1].trim(),
                    email: match[2].trim()
                });
            }
        }
    }
    
    
    let html = '<div class="alert alert-info mt-4" role="alert"><strong>' + searchedFor + '</strong></div>';
    
    if (contacts.length === 0) {
        html += '<div class="alert alert-info mt-4" role="alert">No contacts found</div>';
        resultsDiv.innerHTML = html;
        resultsDiv.style.display = 'block';
        return;
    }
    
    html += '<h5 class="mb-3 mt-4">Search Results (' + contacts.length + ' found)</h5>';
    html += '<div class="table-responsive"><table class="table table-striped table-hover">';
    html += '<thead class="table-dark"><tr><th>UUID</th><th>Email</th></tr></thead><tbody>';
    
    for (let contact of contacts) {
        html += `<tr><td><code>${contact.uuid}</code></td><td>${contact.email}</td></tr>`;
    }
    
    html += '</tbody></table></div>';
    
    resultsDiv.innerHTML = html;
    resultsDiv.style.display = 'block';
    
    // Scroll to results
    setTimeout(() => {
        resultsDiv.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }, 100);
}
