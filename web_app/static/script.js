const REFRESH_INTERVAL = 5 * 60 * 1000; // 5 minutes
const MIDNIGHT_CHECK_INTERVAL = 60 * 1000; // 1 minute

function getUserId() {
    const urlParams = new URLSearchParams(window.location.search);
    return urlParams.get('user_id');
}

function formatMeetingTime(utcTime, timezone = 'Europe/Kiev') {
    return moment.utc(utcTime).tz(timezone).format('HH:mm DD.MM.YYYY');
}

function displayMeeting(meeting) {
    return `
        <div class="meeting">
            <h3>${meeting.title}</h3>
            <p>Thailand: ${formatMeetingTime(meeting.start_time, 'Asia/Bangkok')} - ${formatMeetingTime(meeting.end_time, 'Asia/Bangkok')}</p>
            <p>Ukraine: ${formatMeetingTime(meeting.start_time, 'Europe/Kiev')} - ${formatMeetingTime(meeting.end_time, 'Europe/Kiev')}</p>
            ${meeting.attendants ? `<p>Attendants: ${meeting.attendants.join(', ')}</p>` : ''}
            ${meeting.hangoutLink ? `<p>Link: <a href="${meeting.hangoutLink}">${meeting.hangoutLink}</a></p>` : ''}
            ${meeting.location ? `<p>Location: ${meeting.location}</p>` : ''}
            ${meeting.description ? `<p>Description: ${meeting.description}</p>` : ''}
        </div>
    `;
}

async function fetchMeetings(startDate, endDate) {
    const start = moment(startDate).utc().format();
    const end = moment(endDate).utc().format();
    const response = await fetch(`/api/meetings/?start=${start}&end=${end}`);
    return await response.json();
}

function updateMeetings() {
    const userId = getUserId();
    if (!userId) return;

    fetch(`/meetings?user_id=${userId}`)
        .then(response => response.json())
        .then(data => {
            const container = document.getElementById('meetings-container');
            let html = '';

            if (data.meetings.length === 0) {
                html = `
                    <div class="no-meetings-global">
                        <i class="bi bi-calendar-x"></i>
                        <p>Нет предстоящих встреч на ближайшие дни</p>
                    </div>`;
            } else {
                data.meetings.forEach(day => {
                    html += `
                        <div class="day-section">
                            <h3>
                                <span class="day-name">${day.day_name}</span>
                                <span class="day-date">${day.date}</span>
                            </h3>`;

                    if (day.meetings.length === 0) {
                        html += `
                            <div class="no-meetings-card">
                                <i class="bi bi-calendar-x"></i>
                                <p>Нет встреч на этот день</p>
                            </div>`;
                    } else {
                        day.meetings.forEach(m => {
                            html += `
                                <div class="meeting-card">
                                    <h4>${m.title}</h4>
                                    <div class="time-info">
                                        <div>
                                            <i class="bi bi-globe"></i>
                                            <span class="location-label">Украина:</span>
                                            ${m.start_ua} - ${m.end_ua}
                                        </div>
                                        <div>
                                            <i class="bi bi-globe-asia-australia"></i>
                                            <span class="location-label">Таиланд:</span>
                                            ${m.start_th} - ${m.end_th}
                                        </div>
                                    </div>`;
                            
                            if (m.attendants) {
                                html += `
                                    <div class="meeting-detail">
                                        <i class="bi bi-people"></i>
                                        ${m.attendants}
                                    </div>`;
                            }
                            
                            if (m.location) {
                                html += `
                                    <div class="meeting-detail">
                                        <i class="bi bi-geo-alt"></i>
                                        ${m.location}
                                    </div>`;
                            }
                            
                            if (m.hangoutLink) {
                                html += `
                                    <div class="meeting-detail">
                                        <a href="${m.hangoutLink}" target="_blank" class="meeting-link">
                                            <i class="bi bi-camera-video"></i>
                                            Присоединиться к встрече
                                        </a>
                                    </div>`;
                            }

                            html += `</div>`;
                        });
                    }

                    html += `</div>`;
                });
            }

            container.innerHTML = html;
        })
        .catch(error => console.error('Error fetching meetings:', error));
}

function checkForMidnight() {
    const now = new Date();
    if (now.getHours() === 0 && now.getMinutes() === 0) {
        updateMeetings();
    }
}

document.addEventListener('DOMContentLoaded', () => {
    updateMeetings();
    setInterval(updateMeetings, REFRESH_INTERVAL);
    setInterval(checkForMidnight, MIDNIGHT_CHECK_INTERVAL);
});
