// Pasangan Bekerja dengan Anak
(function() {
    // Helper function to dispatch events for form fields
    function dispatchChangeEvent(element) {
        if (element) {
            element.dispatchEvent(new Event('input', { bubbles: true }));
            element.dispatchEvent(new Event('change', { bubbles: true }));
        }
    }

    // Property Basics
    const propertyType = document.getElementById('type');
    if (propertyType) {
        propertyType.value = 'Rumah'; // Or 'Apartemen'
        dispatchChangeEvent(propertyType);
    }

    const preferredCity = document.getElementById('city');
    if (preferredCity) {
        preferredCity.value = 'Depok Kota'; // Choose from available options
        dispatchChangeEvent(preferredCity);
    }

    const landArea = document.getElementById('land_area');
    if (landArea) {
        landArea.value = 250;
        dispatchChangeEvent(landArea);
    }

    const buildingArea = document.getElementById('building_area');
    if (buildingArea) {
        buildingArea.value = 250;
        dispatchChangeEvent(buildingArea);
    }

    const bedrooms = document.getElementById('bedrooms');
    if (bedrooms) {
        bedrooms.value = 3;
        dispatchChangeEvent(bedrooms);
    }

    const bathrooms = document.getElementById('bathrooms');
    if (bathrooms) {
        bathrooms.value = 2;
        dispatchChangeEvent(bathrooms);
    }

    const floors = document.getElementById('floors');
    if (floors) {
        floors.value = 2;
        dispatchChangeEvent(floors);
    }

    // Nearby Amenities Importance (optional, but setting some for demonstration)
    const school = document.getElementById('SCHOOL');
    if (school) {
        school.checked = true;
        dispatchChangeEvent(school);
    }

    const hospital = document.getElementById('HOSPITAL');
    if (hospital) {
        hospital.checked = true;
        dispatchChangeEvent(hospital);
    }

    const transport = document.getElementById('TRANSPORT');
    if (transport) {
        transport.checked = true;
        dispatchChangeEvent(transport);
    }

    const market = document.getElementById('MARKET');
    if (market) {
        market.checked = true;
        dispatchChangeEvent(market);
    }

    // Desired Property Facilities (optional, but setting some for demonstration)
    const facilityAC = document.getElementById('facility_ac');
    if (facilityAC) {
        facilityAC.checked = true;
        dispatchChangeEvent(facilityAC);
    }

    const facilityCarport = document.getElementById('facility_carport');
    if (facilityCarport) {
        facilityCarport.checked = true;
        dispatchChangeEvent(facilityCarport);
    }

    const facilityGarasi = document.getElementById('facility_garasi');
    if (facilityGarasi) {
        facilityGarasi.checked = true;
        dispatchChangeEvent(facilityGarasi);
    }

    const facilityGarden = document.getElementById('facility_garden');
    if (facilityGarden) {
        facilityGarden.checked = true;
        dispatchChangeEvent(facilityGarden);
    }

    const facilityStove = document.getElementById('facility_stove');
    if (facilityStove) {
        facilityStove.checked = true;
        dispatchChangeEvent(facilityStove);
    }

    const facilityOven = document.getElementById('facility_oven');
    if (facilityOven) {
        facilityOven.checked = true;
        dispatchChangeEvent(facilityOven);
    }

    const facilityRefrigerator = document.getElementById('facility_refrigerator');
    if (facilityRefrigerator) {
        facilityRefrigerator.checked = true;
        dispatchChangeEvent(facilityRefrigerator);
    }

    const facilityMicrowave = document.getElementById('facility_microwave');
    if (facilityMicrowave) {
        facilityMicrowave.checked = true;
        dispatchChangeEvent(facilityMicrowave);
    }

    const facilityPAM = document.getElementById('facility_pam');
    if (facilityPAM) {
        facilityPAM.checked = true;
        dispatchChangeEvent(facilityPAM);
    }

    const facilityWaterHeater = document.getElementById('facility_water_heater');
    if (facilityWaterHeater) {
        facilityWaterHeater.checked = true;
        dispatchChangeEvent(facilityWaterHeater);
    }

    const facilityGordyn = document.getElementById('facility_gordyn');
    if (facilityGordyn) {
        facilityGordyn.checked = true;
        dispatchChangeEvent(facilityGordyn);
    }

    console.log('Form fields have been filled.');
})();
