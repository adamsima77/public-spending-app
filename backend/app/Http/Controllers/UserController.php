<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use Illuminate\Http\Response;
use App\Services\UserService;
use App\Models\User;
use App\Http\Resources\UserResource;

class UserController extends Controller
{
    /**
     * Display a listing of the resource.
     */
    public function index(UserService $userService)
    {
        $this->authorizes('viewAny', User::class);
        $users = $userService->getAllUsers();
        return UserResource::collection($users);
    }

    
    //Invite instead of creating like this
    public function store(Request $request, UserService $userService)
    {
        
    }

    /**
     * Display the specified resource.
     */
    public function show(User $user)
    {
        $this->authorize('view', $user);
        return new UserResource($user);
    }

    /**
     * Update the specified resource in storage.
     */
    public function update(Request $request, User $user, UserService $userService)
    {
        $this->authorize('update', $user);
        $validateEntryData = $request->validate([
            'email' => ['sometimes', 'required', 'string', 'email', 'max:255', Rule::unique('users')->ignore($user->id)],
            'password' => ['sometimes', 'required', 'string', Password::min(8)->letters()->mixedCase()->numbers()->symbols()],
            'name' => ['sometimes', 'required', 'string', 'max:255'], 
            'surname' => ['sometimes', 'required', 'string', 'max:255']
        ]);
        $userService->updateUser($user, $validateEntryData);
        return response()->json(['message' => 'Užívateľ bol úspešne upravený !'], Response::HTTP_OK);
    }

    /**
     * Remove the specified resource from storage.
     */
    public function anonymize(User $user, UserService $userService)
    {
        $this->authorize('anonymize', $user);
        $userService->anonymizeUser($user);
        return response()->json(['message' => 'Užívateľ bol úspešne anonymizovaný !'], Response::HTTP_OK);
    }
}
