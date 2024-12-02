function loadSchedule(teacherId) {
    var scrollPosition = window.scrollY;
    sessionStorage.setItem('scrollPosition', scrollPosition);
    window.location.href = `/teachers?teacher_id=${teacherId}`;
}
window.onload = function() {
    var scrollPosition = sessionStorage.getItem('scrollPosition');
    if (scrollPosition) {
        window.scrollTo(0, scrollPosition);
        sessionStorage.removeItem('scrollPosition');
    }
};
function openAddSchedule(teacherId) {
    document.getElementById('addScheduleForm').style.display = 'block';
    document.getElementById('form_teacher_id').value = teacherId;
}
function closeAddSchedule() {
    document.getElementById('addScheduleForm').style.display = 'none';
}
function deleteSchedule(scheduleId) {
    if (confirm('Вы уверены, что хотите удалить это расписание?')) {
        fetch(`/teachers/delete_schedule?schedule_id=${scheduleId}`, { method: 'POST' })
            .then(response => {
                if (response.ok) {
                    location.reload();
                } else {
                    alert('Ошибка при удалении расписания.');
                }
            });
    }
}