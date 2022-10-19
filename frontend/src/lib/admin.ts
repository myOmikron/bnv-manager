export interface ClubAdminResponse {
    username: null | string,
    error: null | string,
    success: boolean
}

export interface ClubAdmin {
    username: string;
    firstname: string;
    surname: string;
}

export interface Club {
    id: string;
    name: string;
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

export async function getClubAdmins(club_id: string): Promise<ClubAdmin[]> {
    let response = await fetch("/api/clubadmins?club_id="
        + encodeURIComponent(club_id));
    if (!response.ok)
        throw new Error(await response.text());

    let json = await response.json();
    return json.club_admins;
}

export async function getClubs(): Promise<Club[]> {
    let response = await fetch("/api/clubs");
    if (!response.ok)
        throw new Error(await response.text());

    let json = await response.json();
    return json.clubs.map((c: {club_id: string, club_name: string}): Club => ({
        id: c.club_id,
        name: c.club_name
    }));
}

export async function createClub(id: string, name: string): Promise<Club> {
    let response = await fetch("/api/clubs", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            club_id: id,
            club_name: name,
        })
    });
    if (!response.ok)
        throw new Error(await response.text());

    return {
        id: id,
        name: name,
    };
}

export async function deleteClub(id: string): Promise<void> {
    let response = await fetch("/api/clubs?club_id=" + encodeURIComponent(id), {
        method: "DELETE"
    });
    if (!response.ok)
        throw new Error(await response.text());
}
