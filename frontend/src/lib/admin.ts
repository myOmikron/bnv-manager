export interface ClubAdminResponse {
    username: null | string,
    error: null | string,
    success: boolean
}

export async function createClubAdmin(firstname: string, surname: string, password: string, club_id: string): Promise<ClubAdminResponse> {
    let response = await fetch("/api/clubadmins", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            firstname: firstname,
            surname: surname,
            password: password,
            club_id: club_id
        })
    });
    if (!response.ok)
        return {
            username: null,
            error: await response.text(),
            success: false
        };

    let json = await response.json();
    return {
        username: json.username,
        error: null,
        success: true
    }
}
