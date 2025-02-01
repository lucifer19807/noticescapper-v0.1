// static/js/scripts.js

document.addEventListener('DOMContentLoaded', function() {
    fetchNotices();

    const downloadAllBtn = document.getElementById('download-all-btn');
    downloadAllBtn.addEventListener('click', downloadAllNotices);
});

function fetchNotices() {
    fetch('/api/notices')
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                displayError(data.error);
                return;
            }
            populateNotices(data);
        })
        .catch(error => {
            displayError('Failed to fetch notices.');
            console.error(error);
        });
}

function populateNotices(notices) {
    const noticeList = document.getElementById('notice-list');
    noticeList.innerHTML = ''; // Clear existing notices

    notices.forEach((notice, index) => {
        const li = document.createElement('li');

        const titleLink = document.createElement('a');
        titleLink.href = notice.link;
        titleLink.textContent = notice.title;
        titleLink.target = '_blank'; // Open in new tab

        li.appendChild(titleLink);

        if (notice.filename) {
            const downloadBtn = document.createElement('button');
            downloadBtn.textContent = 'Download';
            downloadBtn.classList.add('download-btn');
            downloadBtn.addEventListener('click', () => downloadNotice(notice.filename));
            li.appendChild(downloadBtn);
        } else if (notice.error) {
            const errorMsg = document.createElement('span');
            errorMsg.textContent = 'Download Failed';
            errorMsg.style.color = 'red';
            li.appendChild(errorMsg);
        }

        noticeList.appendChild(li);
    });
}

function downloadNotice(filename) {
    const link = document.createElement('a');
    link.href = `/download/${filename}`;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}

function downloadAllNotices() {
    fetch('/api/notices')
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                alert('Error: ' + data.error);
                return;
            }
            data.forEach(notice => {
                if (notice.filename) {
                    downloadNotice(notice.filename);
                }
            });
        })
        .catch(error => {
            alert('Failed to download all notices.');
            console.error(error);
        });
}

function displayError(message) {
    const noticeList = document.getElementById('notice-list');
    noticeList.innerHTML = `<li style="color: red;">${message}</li>`;
}