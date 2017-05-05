# lighting control passthough (halcyon and xim)
# Ben Hussey - Sept 16

# Halcyon Rooms
ROOMS = {
    2: "Lounge",
    3: "Office",
    4: "Kitchen",
}

# Lighting States
STATES = {
    0: {
        "name": "Party",
        "halcyon_levels": {
            2: 40, # Lounge
            3: 40, # Office
            4: 20, # Kitchen
        },
        "xim_levels": [
            ([12,], 0), # Lampshade
            ([5,], 100), # Pendant
            ([1,2,3,4,6,7,8,9,10,11,], 50), # Spots
        ]
    },
    1: {
        "name": "Work",
        "halcyon_levels": {
            2: 80, # Lounge
            3: 100, # Office
            4: 80, # Kitchen
        },
        "xim_levels": [
            ([12,], 50), # Lampshade
            ([5,], 50), # Pendant
            ([1,2,3,4,6,7,8,9,10,11,], 100), # Spots
        ]
    },
    2: {
        "name": "Relax",
        "halcyon_levels": {
            2: 80, # Lounge
            3: 40, # Office
            4: 40, # Kitchen
        },
        "xim_levels": [
            ([12,], 100), # Lampshade
            ([5,], 50), # Pendant
            ([1,2,3,4,6,7,8,9,10,11,], 50), # Spots
        ]
    },
    3: {
        "name": "Sleep",
        "halcyon_levels": {
            2: 5, # Lounge
            3: 0, # Office
            4: 5, # Kitchen
        },
        "xim_levels": [
            ([12,], 0), # Lampshade
            ([5,], 0), # Pendant
            ([1,2,3,4,6,7,8,9,10,11,], 0), # Spots
        ]
    },
}
