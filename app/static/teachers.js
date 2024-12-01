function loadSchedule(teacherId) {
    // Сохраняем текущую позицию прокрутки
    var scrollPosition = window.scrollY;
    sessionStorage.setItem('scrollPosition', scrollPosition);

    // Перенаправляем на новую страницу с параметром teacher_id
    window.location.href = `/teachers?teacher_id=${teacherId}`;
}

// Восстанавливаем позицию прокрутки после загрузки страницы
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
                    location.reload(); // Перезагрузка страницы после удаления
                } else {
                    alert('Ошибка при удалении расписания.');
                }
            });
    }
}