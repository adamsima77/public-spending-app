<?php

namespace App\Http\Middleware;

use Closure;
use Illuminate\Http\Request;
use Symfony\Component\HttpFoundation\Response;

class CheckIfEtlOrAdmin
{
    /**
     * Handle an incoming request.
     *
     * @param  Closure(Request): (Response)  $next
     */
    public function handle(Request $request, Closure $next): Response
    {
        $providedToken = $request->bearerToken();
        $expectedToken = config('services.etl.api_token', env('PYTHON_ACCESS_KEY'));

        if ($providedToken && hash_equals($expectedToken, $providedToken)) {
            return $next($request);
        }

        $user = $request->user();
        if ($user && $user->isAdmin()) { 
            return $next($request);
        }

        return response()->json([
            'message' => 'K tomuto zdroju nemáte prístup.'
        ], 403);
    }
}
