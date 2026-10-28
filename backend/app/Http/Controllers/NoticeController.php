<?php

declare(strict_types=1);

namespace App\Http\Controllers;

use App\Http\Resources\NoticeResource;
use App\Models\Notice;
use App\Services\NoticeService;
use Illuminate\Http\Resources\Json\AnonymousResourceCollection;

class NoticeController extends Controller
{
    /**
     * Display a listing of the resource.
     */
    public function index(NoticeService $noticeService): AnonymousResourceCollection
    {
        $notices = $noticeService->getNotices();

        return NoticeResource::collection($notices);
    }

    /**
     * Display the specified resource.
     */
    public function show(Notice $notice): NoticeResource
    {
        return new NoticeResource($notice);
    }
}
