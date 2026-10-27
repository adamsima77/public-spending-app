<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        Schema::table('procedures', function (Blueprint $table) {
            $table->string('source_order_id', 32)->nullable();
            $table->index('source_order_id');
            $table->dropUnique(['procedure_reference', 'buyer_id']);
            $table->index(['procedure_reference', 'buyer_id']);
        });
    }

    public function down(): void
    {
        Schema::table('procedures', function (Blueprint $table) {
            $table->dropIndex(['procedure_reference', 'buyer_id']);
            $table->unique(['procedure_reference', 'buyer_id']);

            $table->dropIndex(['source_order_id']);
            $table->dropColumn('source_order_id');
        });
    }
};