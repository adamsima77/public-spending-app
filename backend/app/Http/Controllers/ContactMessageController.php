<?php

declare(strict_types=1);

namespace App\Http\Controllers;

use App\Http\Requests\ContactMessageRequest;
use App\Services\ContactMessageService;
use Illuminate\Http\Response;

class ContactMessageController extends Controller
{
    public function store(ContactMessageRequest $request, ContactMessageService $contactMessageService)
    {
        $validatedData = $request->validated();
        $contactMessageService->createContactMessage($validatedData);

        return response()->json(['message' => 'Contact message created successfully.'], Response::HTTP_CREATED);
    }
}
