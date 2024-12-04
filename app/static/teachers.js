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
function deleteTeacher(teacherId) {
    if (confirm("Вы уверены, что хотите удалить учителя?")) {
        fetch(`/teachers/delete_teacher?teacher_id=${teacherId}`, { method: 'POST' })
            .then(response => {
                if (response.ok) {
                    window.location.reload();
                } else {
                    alert("Ошибка при удалении учителя.");
                }
            });
    }
}
function openAddTeacher() {
    document.getElementById('addTeacherOverlay').style.display = 'block';
}
function closeAddTeacher() {
    document.getElementById('addTeacherOverlay').style.display = 'none';
}
function openEditTeacher(teacherId, firstName, lastName, dateOfBirth, gender, address, phone, email) {
    console.log(document.getElementById('edit_teacher_id').value);
    document.getElementById('editTeacherOverlay').style.display = 'block';
    document.getElementById('edit_teacher_id').value = teacherId;
    document.getElementById('edit_first_name').value = firstName;
    document.getElementById('edit_last_name').value = lastName;
    document.getElementById('edit_date_of_birth').value = dateOfBirth;
    document.getElementById('edit_gender').value = gender;
    document.getElementById('edit_address').value = address;
    document.getElementById('edit_phone').value = phone;
    document.getElementById('edit_email').value = email;
}
function closeEditTeacher() {
    document.getElementById('editTeacherOverlay').style.display = 'none';
}