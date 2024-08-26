document.addEventListener('DOMContentLoaded', function () {
    var formset = document.getElementById('image-formset');
    var addButton = document.getElementById('add-form-row');
    var totalFormsInput = formset.querySelector('input[name$="TOTAL_FORMS"]');  // Using a more flexible selector

    if (!totalFormsInput) {
        console.error("Management form 'TOTAL_FORMS' input not found.");
        return;
    }

    addButton.addEventListener('click', function () {
        var formCount = parseInt(totalFormsInput.value);
        var newForm = formset.querySelector('.form-row:last-child').cloneNode(true);

        // Clear values in the cloned form
        Array.from(newForm.querySelectorAll('input')).forEach(function (input) {
            input.value = '';
            // Update the name and id to the new form count
            var name = input.name.replace(/form-(\d+)-/, 'form-' + formCount + '-');
            var id = input.id.replace(/form-(\d+)-/, 'form-' + formCount + '-');
            input.name = name;
            input.id = id;
        });

        // Append the new form to the formset
        formset.appendChild(newForm);

        // Increment the total number of forms
        totalFormsInput.value = formCount + 1;
    });

    formset.addEventListener('click', function (e) {
        if (e.target.classList.contains('remove-form-row')) {
            e.preventDefault();

            // Only remove if there's more than one form remaining
            if (formset.querySelectorAll('.form-row').length > 1) {
                e.target.parentNode.remove();
                // Decrement the total number of forms
                totalFormsInput.value = parseInt(totalFormsInput.value) - 1;
            }
        }
    });
});
