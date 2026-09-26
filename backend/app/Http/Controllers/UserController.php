<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use Illuminate\Http\Response;
use App\Services\UserService;
use App\Models\User;
use App\Http\Resources\UserResource;
use App\Http\Requests\UpdateUserRequest;

class UserController extends Controller
{
    /**
     * Display a listing of the resource.
     */
    public function index(UserService $userService)
    {
        $this->authorize('viewAny', User::class);
        $users = $userService->getAllUsers();
        return UserResource::collection($users);
    }


    //Invite instead of creating like this
    public function invite(Request $request, UserService $userService)
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
    public function update(UpdateUserRequest $request, User $user, UserService $userService)
    {
        $this->authorize('update', $user);
        $validateEntryData = $request->validated();
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
