<?php

declare(strict_types=1);

namespace App\Http\Controllers;

use App\Http\Requests\UpdateUserRequest;
use App\Http\Resources\UserResource;
use App\Models\User;
use App\Services\UserService;
use Illuminate\Http\JsonResponse;
use Illuminate\Http\Request;
use Illuminate\Http\Resources\Json\AnonymousResourceCollection;
use Illuminate\Http\Response;

class UserController extends Controller
{
    /**
     * Display a listing of the resource.
     */
    public function index(UserService $userService): AnonymousResourceCollection
    {
        $this->authorize('viewAny', User::class);
        $users = $userService->getAllUsers();

        return UserResource::collection($users);
    }

    // Invite instead of creating like this
    public function invite(Request $request, UserService $userService): void {}

    /**
     * Display the specified resource.
     */
    public function show(User $user): UserResource
    {
        $this->authorize('view', $user);

        return new UserResource($user);
    }

    /**
     * Update the specified resource in storage.
     */
    public function update(UpdateUserRequest $request, User $user, UserService $userService): JsonResponse
    {
        $this->authorize('update', $user);
        $validateEntryData = $request->validated();
        $userService->updateUser($user, $validateEntryData);

        return response()->json(['message' => 'Užívateľ bol úspešne upravený !'], Response::HTTP_OK);
    }

    /**
     * Remove the specified resource from storage.
     */
    public function anonymize(User $user, UserService $userService): JsonResponse
    {
        $this->authorize('anonymize', $user);
        $userService->anonymizeUser($user);

        return response()->json(['message' => 'Užívateľ bol úspešne anonymizovaný !'], Response::HTTP_OK);
    }
}
